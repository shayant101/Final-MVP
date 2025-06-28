#!/usr/bin/env python3.9
"""
Restaurant Database Cleanup and Realistic Data Seeding Script
Removes all test restaurants and creates realistic sample data
"""
import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from faker import Faker
import uuid

from app.database import connect_to_mongo, get_database
from app.auth import get_password_hash
from app.models import UserRole, CampaignType, CampaignStatus, ChecklistStatus

# Initialize Faker for realistic data generation
fake = Faker('en_US')

class RestaurantDataSeeder:
    def __init__(self):
        self.db = None
        self.users_collection = None
        self.restaurants_collection = None
        self.campaigns_collection = None
        self.checklist_status_collection = None
        self.restaurant_checklist_status_collection = None
        
    async def initialize(self):
        """Initialize database connection and collections"""
        await connect_to_mongo()
        self.db = get_database()
        self.users_collection = self.db.users
        self.restaurants_collection = self.db.restaurants
        self.campaigns_collection = self.db.campaigns
        self.checklist_status_collection = self.db.checklist_status
        self.restaurant_checklist_status_collection = self.db.restaurant_checklist_status
        
    async def cleanup_test_data(self):
        """Remove all existing test restaurants and related data"""
        print("🧹 Starting cleanup of test restaurant data...")
        
        try:
            # Get all restaurant users
            restaurant_users = await self.users_collection.find({"role": "restaurant"}).to_list(length=None)
            restaurant_user_ids = [str(user["_id"]) for user in restaurant_users]
            
            # Get all restaurants
            restaurants = await self.restaurants_collection.find({}).to_list(length=None)
            restaurant_ids = [str(restaurant["_id"]) for restaurant in restaurants]
            
            print(f"📊 Found {len(restaurant_users)} restaurant users and {len(restaurants)} restaurants")
            
            # Delete campaigns
            campaign_result = await self.campaigns_collection.delete_many({})
            print(f"🗑️  Deleted {campaign_result.deleted_count} campaigns")
            
            # Delete checklist status entries
            checklist_result = await self.checklist_status_collection.delete_many({})
            print(f"🗑️  Deleted {checklist_result.deleted_count} checklist status entries")
            
            # Delete restaurant checklist status entries
            restaurant_checklist_result = await self.restaurant_checklist_status_collection.delete_many({})
            print(f"🗑️  Deleted {restaurant_checklist_result.deleted_count} restaurant checklist status entries")
            
            # Delete restaurants
            restaurant_delete_result = await self.restaurants_collection.delete_many({})
            print(f"🗑️  Deleted {restaurant_delete_result.deleted_count} restaurants")
            
            # Delete restaurant users (keep admin users)
            user_result = await self.users_collection.delete_many({"role": "restaurant"})
            print(f"🗑️  Deleted {user_result.deleted_count} restaurant users")
            
            print("✅ Cleanup completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during cleanup: {str(e)}")
            raise
    
    def generate_restaurant_types(self) -> List[Dict[str, Any]]:
        """Generate realistic restaurant types and names"""
        restaurant_types = [
            {
                "type": "Italian",
                "names": ["Bella Vista", "Nonna's Kitchen", "Tuscany Bistro", "Roma Trattoria", "Amore Ristorante"],
                "specialties": ["Margherita Pizza", "Fettuccine Alfredo", "Osso Buco", "Tiramisu", "Bruschetta"]
            },
            {
                "type": "Mexican",
                "names": ["Casa Miguel", "El Corazón", "Fiesta Cantina", "Los Amigos", "Azteca Grill"],
                "specialties": ["Fish Tacos", "Carnitas Burrito", "Guacamole", "Enchiladas", "Churros"]
            },
            {
                "type": "Asian",
                "names": ["Golden Dragon", "Sakura Sushi", "Pho Saigon", "Bamboo Garden", "Lotus Kitchen"],
                "specialties": ["Pad Thai", "Sushi Roll", "Ramen Bowl", "General Tso's Chicken", "Dumplings"]
            },
            {
                "type": "American",
                "names": ["The Burger Joint", "Main Street Diner", "Liberty Grill", "Hometown Cafe", "Stars & Stripes"],
                "specialties": ["Classic Burger", "BBQ Ribs", "Mac & Cheese", "Apple Pie", "Buffalo Wings"]
            },
            {
                "type": "Mediterranean",
                "names": ["Olive Branch", "Santorini Cafe", "Mediterranean Breeze", "Aegean Kitchen", "Cyprus Grill"],
                "specialties": ["Gyro Platter", "Hummus & Pita", "Lamb Kebab", "Baklava", "Greek Salad"]
            },
            {
                "type": "French",
                "names": ["Le Petit Bistro", "Café Paris", "Brasserie Lyon", "Chez Antoine", "La Belle Époque"],
                "specialties": ["Coq au Vin", "French Onion Soup", "Crème Brûlée", "Escargot", "Ratatouille"]
            }
        ]
        return restaurant_types
    
    def generate_realistic_restaurant(self, restaurant_type: Dict[str, Any]) -> Dict[str, Any]:
        """Generate realistic restaurant data"""
        name = random.choice(restaurant_type["names"])
        specialty = random.choice(restaurant_type["specialties"])
        
        # Generate realistic business email
        business_name = name.lower().replace(" ", "").replace("'", "").replace("&", "and")
        email_domains = ["gmail.com", "yahoo.com", "outlook.com", "restaurant.com", "business.com"]
        email = f"{business_name}@{random.choice(email_domains)}"
        
        # Generate realistic address
        address = f"{fake.building_number()} {fake.street_name()}, {fake.city()}, {fake.state_abbr()} {fake.zipcode()}"
        
        # Generate realistic phone number
        phone = fake.phone_number()
        
        # Generate signup date within last 6 months
        start_date = datetime.now() - timedelta(days=180)
        end_date = datetime.now() - timedelta(days=1)
        signup_date = fake.date_time_between(start_date=start_date, end_date=end_date)
        
        return {
            "name": name,
            "type": restaurant_type["type"],
            "specialty": specialty,
            "email": email,
            "address": address,
            "phone": phone,
            "signup_date": signup_date
        }
    
    async def create_realistic_campaigns(self, restaurant_id: str, restaurant_data: Dict[str, Any]) -> List[str]:
        """Create realistic campaigns for a restaurant"""
        campaigns = []
        campaign_count = random.randint(0, 4)  # 0-4 campaigns per restaurant
        
        for i in range(campaign_count):
            campaign_type = random.choice([CampaignType.facebook_ad, CampaignType.sms])
            status = random.choice([
                CampaignStatus.active, CampaignStatus.completed, 
                CampaignStatus.paused, CampaignStatus.draft
            ])
            
            # Generate campaign based on type
            if campaign_type == CampaignType.facebook_ad:
                budget = random.randint(50, 500)
                campaign_name = f"{restaurant_data['name']} - {restaurant_data['specialty']} Promotion"
                
                details = {
                    "restaurant_name": restaurant_data["name"],
                    "item_to_promote": restaurant_data["specialty"],
                    "offer": f"{random.randint(10, 30)}% off {restaurant_data['specialty']}",
                    "budget": budget,
                    "ad_copy": f"Try our amazing {restaurant_data['specialty']} at {restaurant_data['name']}!",
                    "promo_code": f"{restaurant_data['specialty'][:3].upper()}{random.randint(10, 99)}",
                    "expected_reach": random.randint(1000, 5000),
                    "estimated_impressions": random.randint(5000, 20000)
                }
            else:  # SMS campaign
                campaign_name = f"{restaurant_data['name']} - Customer Reengagement"
                details = {
                    "restaurant_name": restaurant_data["name"],
                    "offer": f"Come back for {random.randint(15, 25)}% off your next meal!",
                    "offer_code": f"BACK{random.randint(10, 99)}",
                    "messages_sent": random.randint(50, 300),
                    "delivery_rate": f"{random.randint(85, 98)}%",
                    "total_cost": random.randint(25, 150)
                }
            
            # Generate campaign dates
            campaign_date = fake.date_time_between(
                start_date=restaurant_data["signup_date"],
                end_date=datetime.now()
            )
            
            campaign_doc = {
                "campaign_id": str(uuid.uuid4()),
                "restaurant_id": restaurant_id,
                "campaign_type": campaign_type,
                "status": status,
                "name": campaign_name,
                "details": details,
                "budget": details.get("budget", 0),
                "created_at": campaign_date,
                "updated_at": campaign_date,
                "launched_at": campaign_date if status != CampaignStatus.draft else None
            }
            
            result = await self.campaigns_collection.insert_one(campaign_doc)
            campaigns.append(str(result.inserted_id))
        
        return campaigns
    
    async def create_checklist_progress(self, restaurant_id: str, restaurant_data: Dict[str, Any]):
        """Create realistic checklist progress for a restaurant"""
        # Get all checklist items
        checklist_items = await self.db.checklist_items.find({}).to_list(length=None)
        
        if not checklist_items:
            print("⚠️  No checklist items found in database")
            return
        
        # Determine completion rate based on how long restaurant has been signed up
        days_since_signup = (datetime.now() - restaurant_data["signup_date"]).days
        
        # More established restaurants have higher completion rates
        if days_since_signup > 120:  # 4+ months
            completion_rate = random.uniform(0.7, 0.95)
        elif days_since_signup > 60:  # 2+ months
            completion_rate = random.uniform(0.4, 0.8)
        elif days_since_signup > 30:  # 1+ month
            completion_rate = random.uniform(0.2, 0.6)
        else:  # New restaurants
            completion_rate = random.uniform(0.1, 0.4)
        
        for item in checklist_items:
            # Randomly decide if this item is completed based on completion rate
            if random.random() < completion_rate:
                status = ChecklistStatus.completed
            elif random.random() < 0.3:  # 30% chance of in_progress
                status = ChecklistStatus.in_progress
            else:
                status = ChecklistStatus.pending
            
            # Generate realistic update date
            if status != ChecklistStatus.pending:
                update_date = fake.date_time_between(
                    start_date=restaurant_data["signup_date"],
                    end_date=datetime.now()
                )
            else:
                update_date = restaurant_data["signup_date"]
            
            # Create checklist status entry
            status_doc = {
                "restaurant_id": restaurant_id,
                "item_id": item["_id"],
                "status": status,
                "notes": f"Updated by {restaurant_data['name']}" if status == ChecklistStatus.completed else None,
                "last_updated_at": update_date
            }
            
            await self.restaurant_checklist_status_collection.insert_one(status_doc)
    
    async def generate_analytics_data(self, restaurant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate realistic analytics data"""
        days_since_signup = (datetime.now() - restaurant_data["signup_date"]).days
        
        # Base metrics on restaurant age and type
        base_customers = random.randint(50, 200)
        monthly_growth = random.uniform(0.05, 0.25)  # 5-25% monthly growth
        
        # Calculate realistic metrics
        new_customers = max(1, int(base_customers * monthly_growth * (days_since_signup / 30)))
        reengaged_customers = max(1, int(new_customers * random.uniform(0.3, 0.7)))
        
        return {
            "new_customers_acquired": new_customers,
            "customers_reengaged": reengaged_customers,
            "marketing_score": random.randint(65, 95),
            "revenue_growth": random.uniform(0.1, 0.4),
            "customer_retention": random.uniform(0.6, 0.9)
        }
    
    async def seed_realistic_restaurants(self, count: int = 20):
        """Create realistic restaurant data"""
        print(f"🌱 Seeding {count} realistic restaurants...")
        
        restaurant_types = self.generate_restaurant_types()
        created_restaurants = []
        
        try:
            for i in range(count):
                # Select random restaurant type
                restaurant_type = random.choice(restaurant_types)
                restaurant_data = self.generate_realistic_restaurant(restaurant_type)
                
                print(f"📝 Creating restaurant {i+1}/{count}: {restaurant_data['name']}")
                
                # Create user account
                user_data = {
                    "email": restaurant_data["email"],
                    "password_hash": get_password_hash("password123"),  # Default password
                    "role": UserRole.restaurant,
                    "created_at": restaurant_data["signup_date"]
                }
                
                user_result = await self.users_collection.insert_one(user_data)
                user_id = str(user_result.inserted_id)
                
                # Generate analytics data
                analytics = await self.generate_analytics_data(restaurant_data)
                
                # Create restaurant document
                restaurant_doc = {
                    "user_id": user_id,
                    "name": restaurant_data["name"],
                    "address": restaurant_data["address"],
                    "phone": restaurant_data["phone"],
                    "cuisine_type": restaurant_data["type"],
                    "specialty_item": restaurant_data["specialty"],
                    "created_at": restaurant_data["signup_date"],
                    "new_customers_acquired": analytics["new_customers_acquired"],
                    "customers_reengaged": analytics["customers_reengaged"],
                    "marketing_score": analytics["marketing_score"],
                    "revenue_growth": analytics["revenue_growth"],
                    "customer_retention": analytics["customer_retention"]
                }
                
                restaurant_result = await self.restaurants_collection.insert_one(restaurant_doc)
                restaurant_id = str(restaurant_result.inserted_id)
                
                # Create campaigns
                campaigns = await self.create_realistic_campaigns(restaurant_id, restaurant_data)
                
                # Create checklist progress
                await self.create_checklist_progress(restaurant_id, restaurant_data)
                
                created_restaurants.append({
                    "user_id": user_id,
                    "restaurant_id": restaurant_id,
                    "name": restaurant_data["name"],
                    "email": restaurant_data["email"],
                    "campaigns_created": len(campaigns)
                })
                
                print(f"✅ Created {restaurant_data['name']} with {len(campaigns)} campaigns")
            
            print(f"\n🎉 Successfully created {len(created_restaurants)} realistic restaurants!")
            
            # Print summary
            print("\n📊 SEEDING SUMMARY:")
            print("=" * 50)
            for restaurant in created_restaurants:
                print(f"🏪 {restaurant['name']}")
                print(f"   📧 {restaurant['email']}")
                print(f"   📈 {restaurant['campaigns_created']} campaigns")
                print(f"   🔑 Password: password123")
                print()
            
        except Exception as e:
            print(f"❌ Error during seeding: {str(e)}")
            raise
    
    async def verify_seeded_data(self):
        """Verify the seeded data was created correctly"""
        print("🔍 Verifying seeded data...")
        
        try:
            # Count documents
            user_count = await self.users_collection.count_documents({"role": "restaurant"})
            restaurant_count = await self.restaurants_collection.count_documents({})
            campaign_count = await self.campaigns_collection.count_documents({})
            checklist_count = await self.restaurant_checklist_status_collection.count_documents({})
            
            print(f"✅ Restaurant Users: {user_count}")
            print(f"✅ Restaurants: {restaurant_count}")
            print(f"✅ Campaigns: {campaign_count}")
            print(f"✅ Checklist Entries: {checklist_count}")
            
            # Sample some data
            print("\n📋 Sample Restaurant Data:")
            async for restaurant in self.restaurants_collection.find({}).limit(3):
                user = await self.users_collection.find_one({"_id": restaurant["user_id"]})
                campaigns = await self.campaigns_collection.count_documents({"restaurant_id": str(restaurant["_id"])})
                
                print(f"🏪 {restaurant['name']}")
                print(f"   📧 {user['email'] if user else 'N/A'}")
                print(f"   📍 {restaurant['address']}")
                print(f"   🍽️  {restaurant.get('cuisine_type', 'N/A')} - {restaurant.get('specialty_item', 'N/A')}")
                print(f"   📈 {campaigns} campaigns")
                print(f"   📊 Marketing Score: {restaurant.get('marketing_score', 'N/A')}")
                print()
            
        except Exception as e:
            print(f"❌ Error during verification: {str(e)}")
            raise

async def main():
    """Main execution function"""
    print("🚀 Restaurant Database Cleanup and Seeding Tool")
    print("=" * 50)
    
    seeder = RestaurantDataSeeder()
    await seeder.initialize()
    
    try:
        # Phase 1: Cleanup
        await seeder.cleanup_test_data()
        
        print("\n" + "=" * 50)
        
        # Phase 2: Seed realistic data
        await seeder.seed_realistic_restaurants(count=20)
        
        print("\n" + "=" * 50)
        
        # Phase 3: Verify
        await seeder.verify_seeded_data()
        
        print("\n🎉 Database cleanup and seeding completed successfully!")
        print("\n📝 All restaurants use password: password123")
        print("🔐 You can now login to any restaurant using their email and this password")
        
    except Exception as e:
        print(f"\n❌ Script failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())