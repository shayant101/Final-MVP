#!/usr/bin/env python3.9

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.checklist_service import ChecklistService
from app.models import ChecklistStatus
from bson import ObjectId

async def test_persistence():
    """Test if checklist updates are actually persisted to the database"""
    
    service = ChecklistService()
    
    # Use a test restaurant ID - we'll create one if it doesn't exist
    restaurant_id = "676c8b5b4d8c9e1234567890"
    
    print("=== TESTING DATABASE PERSISTENCE ===")
    
    # Step 1: Get initial categories with items
    print("\n1. Getting initial categories with items...")
    try:
        initial_categories = await service.get_categories_with_items(restaurant_id=restaurant_id)
        
        if not initial_categories or not initial_categories[0].get('items'):
            print("❌ No categories or items found")
            return
        
        # Find first item to test
        test_item = initial_categories[0]['items'][0]
        item_id = test_item['item_id']
        initial_status = test_item.get('status', 'pending')
        
        print(f"   Test item: {test_item['title']}")
        print(f"   Initial status: {initial_status}")
        
    except Exception as e:
        print(f"❌ Failed to get categories: {e}")
        return
    
    # Step 2: Update the item status to completed
    print(f"\n2. Updating item {item_id} to 'completed'...")
    try:
        status_id = await service.update_item_status(
            restaurant_id=restaurant_id,
            item_id=item_id,
            status=ChecklistStatus.completed,
            notes="Test update"
        )
        print(f"   ✅ Update successful, status_id: {status_id}")
    except Exception as e:
        print(f"   ❌ Update failed: {e}")
        return
    
    # Step 3: Directly check database
    print(f"\n3. Checking database directly...")
    try:
        status_doc = await service.status_collection.find_one({
            "restaurant_id": ObjectId(restaurant_id),
            "item_id": ObjectId(item_id)
        })
        
        if status_doc:
            print(f"   ✅ Found in database: {status_doc['status']}")
            print(f"   Last updated: {status_doc['last_updated_at']}")
        else:
            print(f"   ❌ NOT found in database!")
            return
    except Exception as e:
        print(f"   ❌ Database check failed: {e}")
        return
    
    # Step 4: Retrieve via get_categories_with_items
    print(f"\n4. Retrieving via get_categories_with_items...")
    try:
        updated_categories = await service.get_categories_with_items(restaurant_id=restaurant_id)
        
        # Find the same item
        updated_item = None
        for category in updated_categories:
            for item in category.get('items', []):
                if item['item_id'] == item_id:
                    updated_item = item
                    break
            if updated_item:
                break
        
        if updated_item:
            retrieved_status = updated_item.get('status', 'pending')
            print(f"   Retrieved status: {retrieved_status}")
            
            if retrieved_status == 'completed':
                print("   ✅ Status correctly retrieved as 'completed'")
                print("   🎯 DATABASE PERSISTENCE IS WORKING CORRECTLY")
            else:
                print(f"   ❌ Status mismatch! Expected 'completed', got '{retrieved_status}'")
                print("   🚨 THIS IS THE BUG - DATABASE WRITE/READ INCONSISTENCY")
        else:
            print("   ❌ Item not found in retrieved data")
            
    except Exception as e:
        print(f"   ❌ Retrieval test failed: {e}")
    
    # Step 5: Test multiple rapid updates (race condition test)
    print(f"\n5. Testing rapid updates (race condition)...")
    try:
        # Rapid fire updates
        await service.update_item_status(restaurant_id, item_id, ChecklistStatus.in_progress)
        await service.update_item_status(restaurant_id, item_id, ChecklistStatus.completed)
        await service.update_item_status(restaurant_id, item_id, ChecklistStatus.completed)
        
        # Check final state
        final_status_doc = await service.status_collection.find_one({
            "restaurant_id": ObjectId(restaurant_id),
            "item_id": ObjectId(item_id)
        })
        
        if final_status_doc and final_status_doc['status'] == 'completed':
            print("   ✅ Rapid updates handled correctly")
        else:
            print(f"   ❌ Rapid updates failed, final status: {final_status_doc['status'] if final_status_doc else 'None'}")
    except Exception as e:
        print(f"   ❌ Rapid update test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_persistence())