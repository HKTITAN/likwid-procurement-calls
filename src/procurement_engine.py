"""
Procurement Engine
Core business logic for vendor selection and procurement automation
"""

import logging
from typing import List, Optional, Tuple, Dict
from datetime import datetime
import uuid

from .models import Vendor, InventoryItem, VendorItemMapping, ProcurementRecord, ProcurementConfig
from .data_manager import DataManager
from .twilio_manager import TwilioManager

logger = logging.getLogger(__name__)


class VendorSelector:
    """Handles vendor selection logic based on multiple criteria"""
    
    def __init__(self, config: ProcurementConfig):
        self.config = config
    
    def calculate_vendor_score(self, vendor_mapping: VendorItemMapping, item: InventoryItem, 
                             total_quantity: int) -> float:
        """
        Calculate vendor score based on multiple factors
        
        Args:
            vendor_mapping: Vendor-item mapping with pricing info
            item: Inventory item being ordered
            total_quantity: Total quantity needed
            
        Returns:
            Calculated score (higher is better)
        """
        # Price score (lower price is better, so invert)
        effective_price = vendor_mapping.get_effective_price(total_quantity)
        total_cost = effective_price * total_quantity
        price_score = 1 / (total_cost / 1000 + 1)  # Normalize price score
        
        # Rating scores (already on 0-5 scale, normalize to 0-1)
        quality_score = vendor_mapping.quality_rating / 5.0
        delivery_score = vendor_mapping.delivery_rating / 5.0
        service_score = vendor_mapping.service_rating / 5.0
        
        # Delivery time score (faster is better)
        delivery_time_score = 1 / (vendor_mapping.lead_time_days / 10 + 1)
        
        # Availability bonus
        availability_bonus = 1.0 if vendor_mapping.availability_status == "In Stock" else 0.5
        
        # Calculate weighted score
        score = (
            self.config.price_weight * price_score +
            self.config.rating_weight * (quality_score + delivery_score + service_score) / 3 +
            self.config.delivery_weight * delivery_time_score +
            self.config.service_weight * availability_bonus
        )
        
        return score
    
    def select_best_vendor_for_item(self, item: InventoryItem, 
                                  vendor_mappings: List[VendorItemMapping],
                                  vendors: Dict[str, Vendor]) -> Optional[Tuple[Vendor, VendorItemMapping, float]]:
        """
        Select the best vendor for a specific item
        
        Args:
            item: Inventory item to source
            vendor_mappings: List of vendor mappings for this item
            vendors: Dictionary of vendor objects
            
        Returns:
            Tuple of (vendor, mapping, score) or None if no suitable vendor found
        """
        if not vendor_mappings:
            logger.warning(f"No vendor mappings found for item {item.item_id}")
            return None
        
        best_vendor = None
        best_mapping = None
        best_score = 0.0
        
        for mapping in vendor_mappings:
            vendor = vendors.get(mapping.vendor_id)
            if not vendor or vendor.status != "Active":
                continue
            
            # Calculate score for this vendor
            score = self.calculate_vendor_score(mapping, item, item.reorder_quantity)
            
            logger.debug(f"Vendor {vendor.vendor_name} score for {item.item_name}: {score:.3f}")
            
            if score > best_score:
                best_score = score
                best_vendor = vendor
                best_mapping = mapping
        
        if best_vendor:
            logger.info(f"Selected vendor {best_vendor.vendor_name} for {item.item_name} (score: {best_score:.3f})")
            return best_vendor, best_mapping, best_score
        
        logger.warning(f"No suitable vendor found for item {item.item_id}")
        return None
    
    def select_vendors_for_items(self, items: List[InventoryItem], data_manager: DataManager) -> Dict[str, Tuple[Vendor, VendorItemMapping, float]]:
        """
        Select best vendors for multiple items
        
        Args:
            items: List of inventory items needing procurement
            data_manager: Data manager instance
            
        Returns:
            Dictionary mapping item_id to (vendor, mapping, score)
        """
        selections = {}
        
        for item in items:
            vendor_mappings = data_manager.get_vendors_for_item(item.item_id)
            selection = self.select_best_vendor_for_item(item, vendor_mappings, data_manager.vendors)
            
            if selection:
                vendor, mapping, score = selection
                selections[item.item_id] = selection
                
                logger.info(f"Selected {vendor.vendor_name} for {item.item_name} "
                          f"at ${mapping.get_effective_price(item.reorder_quantity):.2f} per unit")
        
        return selections


class ProcurementEngine:
    """Main procurement automation engine"""
    
    def __init__(self, config: ProcurementConfig):
        self.config = config
        self.data_manager = DataManager(config)
        self.vendor_selector = VendorSelector(config)
        self.twilio_manager = None
        
        # Initialize Twilio if credentials are available
        if (config.twilio_account_sid and config.twilio_auth_token and 
            "YOUR_TWILIO" not in config.twilio_account_sid):
            self.twilio_manager = TwilioManager(
                config.twilio_account_sid,
                config.twilio_auth_token,
                config.twilio_phone_number,
                config.allowed_phone_number
            )
    
    def check_inventory_and_get_requirements(self) -> List[InventoryItem]:
        """
        Check inventory levels and return items needing reorder
        
        Returns:
            List of items that need reordering
        """
        items_needing_reorder = self.data_manager.get_items_needing_reorder()
        
        logger.info(f"Found {len(items_needing_reorder)} items needing reorder")
        
        for item in items_needing_reorder:
            logger.info(f"Item {item.item_name}: {item.current_stock} units "
                       f"(threshold: {item.min_threshold})")
        
        return items_needing_reorder
    
    def create_procurement_plan(self, items: List[InventoryItem]) -> Dict:
        """
        Create a procurement plan for the given items
        
        Args:
            items: List of items needing procurement
            
        Returns:
            Dictionary containing the procurement plan
        """
        if not items:
            return {"status": "no_items_needed", "items": []}
        
        # Select best vendors for each item
        vendor_selections = self.vendor_selector.select_vendors_for_items(items, self.data_manager)
        
        if not vendor_selections:
            return {"status": "no_vendors_found", "items": []}
        
        # Group items by vendor to minimize number of orders
        vendor_groups = {}
        total_cost = 0.0
        total_items = 0
        
        for item_id, (vendor, mapping, score) in vendor_selections.items():
            item = self.data_manager.get_item_by_id(item_id)
            if not item:
                continue
            
            if vendor.vendor_id not in vendor_groups:
                vendor_groups[vendor.vendor_id] = {
                    'vendor': vendor,
                    'items': [],
                    'total_cost': 0.0,
                    'can_call': vendor.is_authorized_for_calls
                }
            
            item_cost = mapping.get_effective_price(item.reorder_quantity) * item.reorder_quantity
            vendor_groups[vendor.vendor_id]['items'].append({
                'item': item,
                'mapping': mapping,
                'quantity': item.reorder_quantity,
                'unit_price': mapping.get_effective_price(item.reorder_quantity),
                'total_price': item_cost,
                'score': score
            })
            vendor_groups[vendor.vendor_id]['total_cost'] += item_cost
            total_cost += item_cost
            total_items += item.reorder_quantity
        
        return {
            "status": "plan_created",
            "vendor_groups": vendor_groups,
            "total_cost": total_cost,
            "total_items": total_items,
            "requires_approval": total_cost > self.config.auto_approve_threshold
        }
    
    def execute_procurement_plan(self, plan: Dict) -> List[ProcurementRecord]:
        """
        Execute the procurement plan by making calls and creating records
        
        Args:
            plan: Procurement plan from create_procurement_plan
            
        Returns:
            List of procurement records created
        """
        if plan["status"] != "plan_created":
            logger.warning(f"Cannot execute plan with status: {plan['status']}")
            return []
        
        records = []
        
        for vendor_id, group in plan["vendor_groups"].items():
            vendor = group['vendor']
            items = group['items']
            total_cost = group['total_cost']
            
            # Create procurement record
            record = ProcurementRecord(
                record_id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                items_required=[item['item'].item_name for item in items],
                selected_vendor_id=vendor.vendor_id,
                selected_vendor_name=vendor.vendor_name,
                total_cost=total_cost,
                total_items=sum(item['quantity'] for item in items),
                status="initiated",
                approval_required=plan["requires_approval"],
                order_number=f"PO-{datetime.now().strftime('%Y%m%d')}-{vendor_id}"
            )
            
            # Make phone call if vendor is authorized and Twilio is available
            if group['can_call'] and self.twilio_manager:
                item_names = [item['item'].item_name for item in items]
                call_sid = self.twilio_manager.make_procurement_call(
                    vendor.vendor_name,
                    vendor.phone_number,
                    item_names,
                    self.config.company_name
                )
                
                if call_sid and call_sid != "blocked_unauthorized_number":
                    record.call_sid = call_sid
                    record.status = "call_completed"
                    logger.info(f"Call completed for vendor {vendor.vendor_name}, SID: {call_sid}")
                else:
                    record.status = "call_failed"
                    logger.warning(f"Call failed for vendor {vendor.vendor_name}")
            else:
                if not group['can_call']:
                    record.status = "call_blocked_unauthorized"
                    logger.warning(f"Call blocked for unauthorized vendor {vendor.vendor_name}")
                else:
                    record.status = "call_unavailable"
                    logger.warning("Twilio not available for calls")
            
            # Add record to data manager
            self.data_manager.add_procurement_record(record)
            records.append(record)
            
            logger.info(f"Created procurement record {record.record_id} for vendor {vendor.vendor_name}")
        
        return records
    
    def run_full_procurement_cycle(self) -> Dict:
        """
        Run the complete procurement cycle
        
        Returns:
            Summary of the procurement cycle execution
        """
        logger.info("Starting full procurement cycle")
        
        # Step 1: Check inventory
        items_needed = self.check_inventory_and_get_requirements()
        if not items_needed:
            return {
                "status": "completed",
                "message": "No items need reordering",
                "items_processed": 0,
                "orders_created": 0,
                "calls_made": 0
            }
        
        # Step 2: Create procurement plan
        plan = self.create_procurement_plan(items_needed)
        if plan["status"] != "plan_created":
            return {
                "status": "failed",
                "message": f"Failed to create plan: {plan['status']}",
                "items_processed": len(items_needed),
                "orders_created": 0,
                "calls_made": 0
            }
        
        # Step 3: Execute procurement plan
        records = self.execute_procurement_plan(plan)
        
        # Count successful calls
        calls_made = sum(1 for record in records if record.call_sid and record.call_sid != "blocked_unauthorized_number")
        
        # Export results
        self.data_manager.export_to_csv()
        
        logger.info(f"Procurement cycle completed: {len(records)} orders, {calls_made} calls made")
        
        return {
            "status": "completed",
            "message": f"Processed {len(items_needed)} items, created {len(records)} orders",
            "items_processed": len(items_needed),
            "orders_created": len(records),
            "calls_made": calls_made,
            "total_cost": plan["total_cost"],
            "records": records
        }
    
    def get_system_status(self) -> Dict:
        """Get current system status and statistics"""
        stats = self.data_manager.get_summary_stats()
        items_needing_reorder = len(self.data_manager.get_items_needing_reorder())
        
        return {
            "system_ready": bool(self.twilio_manager),
            "twilio_configured": bool(self.twilio_manager),
            "items_needing_reorder": items_needing_reorder,
            "authorized_vendors": stats["authorized_vendors"],
            **stats
        }
