
import firebase_admin
from firebase_admin import credentials, firestore
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def initialize_firebase():
    # Helper to find credentials
    creds_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'miayis-service-account.json')
    if not os.path.exists(creds_path):
        # Update path to where it was seen in file list
        creds_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'wishyahope', 'miayis-service-account.json')
    
    # Try one more location based on file list from step 4
    if not os.path.exists(creds_path):
         creds_path = os.path.join('C:\\Users\\faxys\\OneDrive\\Desktop\\wishyahope\\miayis-service-account.json')

    if not os.path.exists(creds_path):
        print(f"Error: Credentials file not found at {creds_path}")
        sys.exit(1)

    try:
        cred = credentials.Certificate(creds_path)
        firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        sys.exit(1)

def get_scrape_errors():
    db = initialize_firebase()
    
    print(f"{'Timestamp':<20} | {'Status':<8} | {'Code':<15} | {'URL':<50} | {'Reason'}")
    print("-" * 120)

    try:
        # Query for failed or partial status
        # Note: Firestore 'in' queries are limited to 10 items, but we only have 2 values usually
        # REMOVED order_by to avoid index requirement
        docs = db.collection('product_import_issues')\
            .where('status', 'in', ['failed', 'partial'])\
            .limit(100)\
            .stream()
        
        # Convert to list and sort by created_at desc
        results = []
        for doc in docs:
            data = doc.to_dict()
            results.append(data)
            
        # Sort in memory
        results.sort(key=lambda x: x.get('created_at', datetime.min) if x.get('created_at') else datetime.min, reverse=True)
        
        count = 0
        for data in results:
            
            # Format timestamp
            ts = data.get('created_at')
            if ts:
                if hasattr(ts, 'timestamp'):
                    dt = datetime.fromtimestamp(ts.timestamp())
                else:
                    dt = ts
                ts_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            else:
                ts_str = "N/A"
            
            url = data.get('url', 'N/A')
            # if len(url) > 47:
            #     url = url[:47] + "..."
                
            reason = data.get('reason', 'N/A')
            reason = reason.replace('\n', ' ')
            if len(reason) > 50:
                reason = reason[:50] + "..."

            print(f"{ts_str:<20} | {data.get('status', 'N/A'):<8} | {data.get('error_code', 'N/A'):<15} | {url} | {reason}")
            count += 1
            
        if count == 0:
            print("No scrape errors found.")
            
    except Exception as e:
        print(f"Error querying Firestore: {e}")

if __name__ == "__main__":
    get_scrape_errors()
