
import sys
import os
import asyncio
from typing import List, Dict

# Setup paths
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
kataloggia_dir = os.path.join(project_root, 'kataloggia-main')

if project_root not in sys.path:
    sys.path.insert(0, project_root)
# Add kataloggia-main to path explicitly for app imports
if kataloggia_dir not in sys.path:
    sys.path.insert(0, kataloggia_dir)

# Set Firebase credentials path explicitly
if not os.environ.get('FIREBASE_CREDENTIALS_PATH'):
    creds_path = os.path.join(kataloggia_dir, 'miayis-service-account.json')
    if os.path.exists(creds_path):
        os.environ['FIREBASE_CREDENTIALS_PATH'] = creds_path
        print(f"Set FIREBASE_CREDENTIALS_PATH to: {creds_path}")
    else:
        print(f"Warning: Credentials file not found at {creds_path}")

# Import app components (after setting env var)
try:
    from app.services.scraping_service import ScrapingService
    from app.repositories import get_repository
    # Initialize repository
    repo = get_repository()
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def retry_failed_scrapes():
    print("🚀 Starting Retry Process for Failed Scrapes...")
    
    # 1. Fetch all unresolved issues with 'failed' status
    # Note: Using direct firestore access as specific filtered query might not be in repo interface
    try:
        issues_ref = repo.db.collection('product_import_issues')
        query = issues_ref.where('status', '==', 'failed').where('resolved', '==', False)
        
        # Limit to avoid timeouts if there are thousands
        docs = query.limit(50).stream()
        
        issues = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            issues.append(data)
            
    except Exception as e:
        print(f"❌ Error fetching issues: {e}")
        return

    print(f"Found {len(issues)} failed issues to retry.")
    
    scraping_service = ScrapingService()
    success_count = 0
    fail_count = 0
    
    for i, issue in enumerate(issues, 1):
        url = issue.get('url')
        user_id = issue.get('user_id')
        issue_id = issue.get('id')
        current_retry_count = issue.get('retry_count', 0)
        
        print(f"\n[{i}/{len(issues)}] Retrying: {url}")
        
        # Update retry count (optimistic)
        repo.update_import_issue_retry(issue_id, current_retry_count + 1)
        
        try:
            # 2. Attempt Scrape
            scraped_data = scraping_service.scrape_product(url)
            
            if scraped_data:
                print("   ✅ Scrape Successful!")
                
                # 3. Create Product
                try:
                    product_id = repo.create_product(
                        user_id=user_id,
                        name=scraped_data['name'],
                        price=scraped_data['price'],
                        image=scraped_data['image'],
                        brand=scraped_data['brand'],
                        url=url,
                        created_at=None, # will use server timestamp
                        old_price=scraped_data.get('old_price'),
                        current_price=None,
                        discount_percentage=None,
                        images=scraped_data.get('images'),
                        discount_info=scraped_data.get('discount_message')
                    )
                    
                    if product_id:
                        print(f"   🎉 Product created: {product_id}")
                        # 4. Mark as Resolved
                        repo.mark_import_issue_resolved(issue_id)
                        success_count += 1
                    else:
                        print("   ❌ Failed to create product in DB.")
                        fail_count += 1
                        
                except Exception as create_err:
                     print(f"   ❌ Error creating product: {create_err}")
                     fail_count += 1
            else:
                print("   ❌ Scrape returned None (Still failing).")
                fail_count += 1
                
        except Exception as e:
            print(f"   ❌ Exception during retry: {e}")
            fail_count += 1
            
    print(f"\n✨ Retry Complete!")
    print(f"Total processed: {len(issues)}")
    print(f"Success: {success_count}")
    print(f"Still failing: {fail_count}")

if __name__ == "__main__":
    retry_failed_scrapes()
