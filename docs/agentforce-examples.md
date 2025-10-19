# AgentForce Integration Examples

## Example Agent Conversations

### Customer Service Scenario
```
Customer: "Hi, I need to see all my autopayments"
Agent: "I can help you find your autopayments! Let me search for those now."

[Agent calls search_content with classes=autopayment, customer_id=C123]

Agent: "I found 2 autopayments for you:
1. $79.99 to Verizon on the 15th monthly from Credit card ending in 4242
2. $55.00 to GymPro on the 1st monthly from Credit card ending in 7676

Would you like me to help you modify any of these payments?"
```

### Banking Assistant Scenario
```
User: "Show me all closed services for customer C456"
Agent: "I'll search for closed services for customer C456."

[Agent calls search_content with status=closed, customer_id=C456]

Agent: "I found 1 closed service:
- Closed Roth IRA at Delta Funds (transferred out 2024-12-31)

This account was closed recently. Would you like me to help you open a new investment account?"
```

## Advanced Agent Instructions

### Detailed Agent Prompt
```
You are a Banking Services Assistant for ABC Bank. Your role is to help customers and staff find information about banking services.

CAPABILITIES:
- Search for Standing Instructions (recurring transfers between accounts)
- Find Autopayments (scheduled bill payments to external companies)
- Locate Service Links (connections to external financial services)

CONVERSATION STYLE:
- Be friendly and professional
- Explain banking terms in simple language
- Always confirm customer identity before showing sensitive information
- Offer next steps after providing information

WHEN TO USE SEARCH:
1. Customer asks about "payments", "transfers", or "autopay"
2. Staff needs to review customer's banking services
3. Someone wants to find "linked accounts" or "connected services"

SEARCH PARAMETERS:
- classes: Use "autopayment" for bill payments, "standing_instruction" for transfers, "service_link" for connected accounts
- customer_id: Always use when customer is identified
- status: Use "active" for current services, "closed" for historical

EXAMPLE RESPONSES:
After finding results, explain what each service does and ask if they need help managing them.
```

## Flow Integration Alternative

### Screen Flow Configuration
```yaml
Flow Name: Banking Content Search
Type: Screen Flow

Screen 1: "Customer Information"
- Input: Customer ID (Text, Required)
- Input: Service Type (Picklist: All, Autopayments, Standing Instructions, Service Links)
- Input: Status Filter (Picklist: All, Active, Closed)

Action 1: "Call Content Search API"
- External Service: ContentMCPService
- Action: search_content
- Parameters:
  - classes: {!ServiceType}
  - customer_id: {!CustomerID}  
  - status: {!StatusFilter}

Screen 2: "Search Results"
- Display: Search results in data table
- Action: "Search Again" (loops back to Screen 1)
- Action: "Done" (ends flow)
```

## Custom Apex Integration

### Apex Class Example
```apex
public class ContentSearchController {
    
    @AuraEnabled
    public static ContentSearchResponse searchContent(String classes, String customerId, String status) {
        
        // Build request
        HttpRequest req = new HttpRequest();
        String endpoint = 'callout:ContentMCPServer/api/v1/content';
        endpoint += '?classes=' + EncodingUtil.urlEncode(classes, 'UTF-8');
        
        if (String.isNotBlank(customerId)) {
            endpoint += '&customer_id=' + EncodingUtil.urlEncode(customerId, 'UTF-8');
        }
        if (String.isNotBlank(status)) {
            endpoint += '&status=' + EncodingUtil.urlEncode(status, 'UTF-8');
        }
        
        req.setEndpoint(endpoint);
        req.setMethod('GET');
        req.setHeader('Content-Type', 'application/json');
        
        // Make call
        Http http = new Http();
        HttpResponse res = http.send(req);
        
        if (res.getStatusCode() == 200) {
            return (ContentSearchResponse) JSON.deserialize(res.getBody(), ContentSearchResponse.class);
        } else {
            throw new CalloutException('API call failed: ' + res.getBody());
        }
    }
    
    public class ContentSearchResponse {
        public Boolean success;
        public Integer count;
        public List<ContentItem> data;
        public Metadata metadata;
    }
    
    public class ContentItem {
        public String id;
        public String cls;
        public String text;
        public Map<String, String> indexes;
    }
    
    public class Metadata {
        public List<String> classes_searched;
        public Map<String, List<String>> filters_applied;
        public Integer total_limit;
    }
}
```

## Lightning Web Component

### LWC for Customer Service Console
```javascript
// contentSearchComponent.js
import { LightningElement, track } from 'lwc';
import searchContent from '@salesforce/apex/ContentSearchController.searchContent';

export default class ContentSearchComponent extends LightningElement {
    @track customerId = '';
    @track serviceType = 'standing_instruction,autopayment,service_link';
    @track status = '';
    @track results = [];
    @track isLoading = false;
    @track error = '';

    serviceTypeOptions = [
        { label: 'All Services', value: 'standing_instruction,autopayment,service_link' },
        { label: 'Autopayments', value: 'autopayment' },
        { label: 'Standing Instructions', value: 'standing_instruction' },
        { label: 'Service Links', value: 'service_link' }
    ];

    statusOptions = [
        { label: 'All', value: '' },
        { label: 'Active', value: 'active' },
        { label: 'Closed', value: 'closed' }
    ];

    handleInputChange(event) {
        const field = event.target.dataset.field;
        this[field] = event.target.value;
    }

    async handleSearch() {
        this.isLoading = true;
        this.error = '';
        
        try {
            const response = await searchContent({
                classes: this.serviceType,
                customerId: this.customerId,
                status: this.status
            });
            
            this.results = response.data || [];
        } catch (error) {
            this.error = error.body.message;
            this.results = [];
        } finally {
            this.isLoading = false;
        }
    }
}
```

## Agent Deployment Strategies

### 1. Customer Self-Service Portal
```
Experience Cloud Site → Add Agent
- Customers can search their own banking services
- Implement customer authentication
- Limit results to customer's data only
```

### 2. Service Console Integration
```
Service Console → Add Agent as Utility Bar
- Customer service reps use during calls
- Quick access to customer banking info
- Integrated with case management
```

### 3. Mobile App Integration
```
Salesforce Mobile → Add Agent
- Field staff can access customer info
- Voice-activated banking service lookup
- Offline capability for cached results
```

## Performance Optimization

### Caching Strategy
```apex
// Cache frequently accessed data
public class ContentCache {
    private static Map<String, Object> cache = new Map<String, Object>();
    private static final Integer CACHE_TIMEOUT = 300; // 5 minutes
    
    public static Object getCached(String key) {
        // Implementation for caching API responses
        return cache.get(key);
    }
    
    public static void putCached(String key, Object value) {
        cache.put(key, value);
    }
}
```

### Batch Processing
```apex
// For bulk customer data processing
public class ContentBatchProcessor implements Database.Batchable<String> {
    
    public List<String> start(Database.BatchableContext bc) {
        // Return list of customer IDs to process
        return new List<String>{'C123', 'C456', 'C789'};
    }
    
    public void execute(Database.BatchableContext bc, List<String> customerIds) {
        for (String customerId : customerIds) {
            // Process each customer's banking data
            ContentSearchController.searchContent('standing_instruction,autopayment,service_link', customerId, 'active');
        }
    }
    
    public void finish(Database.BatchableContext bc) {
        // Cleanup and notifications
    }
}
```

## Monitoring and Analytics

### Custom Objects for Tracking
```sql
-- Search_Log__c object
CREATE CUSTOM OBJECT Search_Log__c (
    Customer_ID__c TEXT(50),
    Search_Classes__c TEXT(255),
    Results_Count__c NUMBER(5,0),
    Search_Timestamp__c DATETIME,
    User_ID__c LOOKUP(User),
    Response_Time_MS__c NUMBER(8,0)
);
```

### Einstein Analytics Dashboard
```json
{
    "dashboardName": "Banking Service Usage",
    "widgets": [
        {
            "title": "Most Searched Services",
            "type": "bar",
            "query": "SELECT Search_Classes__c, COUNT(Id) FROM Search_Log__c GROUP BY Search_Classes__c"
        },
        {
            "title": "Search Volume Over Time", 
            "type": "line",
            "query": "SELECT DAY_ONLY(Search_Timestamp__c), COUNT(Id) FROM Search_Log__c GROUP BY DAY_ONLY(Search_Timestamp__c)"
        }
    ]
}
```
