🔗 HubSpot CRM Integration ServiceThis project is a standalone FastAPI microservice designed to synchronize data between a local Help Desk system and HubSpot CRM. It handles the synchronization of Contacts and Tickets, ensuring that support agents and sales teams always see the same up-to-date information.🧐 1. Which CRM I Chose & WhyI chose HubSpot CRM for this integration.Why HubSpot?Developer-Friendly API: HubSpot offers a robust, well-documented REST API (v3) with clear endpoints for standard objects like Contacts and Tickets.Free Tier Access: The CRM functionality is available for free, making it ideal for development and testing without incurring costs.Scalability: It supports custom properties and high API rate limits, which mimics a real-world enterprise environment.Comprehensive Ecosystem: It includes built-in tools for email tracking, ticketing pipelines, and customer management, providing a complete "backend" for a support desk.⚙️ 2. Configuration & SetupPrerequisitesPython 3.9+A HubSpot Developer Account (or a standard account with a Private App created)pip (Python Package Manager)InstallationClone the Repository:Bashgit clone <your-repo-url>
cd CRM-integration
Create a Virtual Environment:Bashpython -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
Install Dependencies:Bashpip install -r requirements.txt
Setting up CredentialsCreate a file named .env in the root directory.Add your HubSpot Private App Access Token:Code snippetHUBSPOT_ACCESS_TOKEN=pat-na1-blablabla...
HUBSPOT_BASE_URL=https://api.hubapi.com
To get your token: Go to HubSpot Settings > Integrations > Private Apps > Create a Private App.Scopes required:crm.objects.contacts.readcrm.objects.contacts.writecrm.objects.tickets.readcrm.objects.tickets.write🚀 3. How to Run the Sync & What to ExpectThis service acts as a bridge. It does not run a continuous background loop; instead, it provides REST API endpoints that the main Support Desk application calls whenever data needs to be synced.Start the ServerRun the FastAPI server using Uvicorn:Bashuvicorn main:app --reload --port 8000
The API will be available at: http://localhost:8000Interactive API Docs (Swagger UI): http://localhost:8000/docsSync Behavior (What to Expect)ActionAPI EndpointBehaviorCreate ContactPOST /integrate/contactCreates a contact in HubSpot. If the email already exists, it returns the existing HubSpot ID to prevent duplicates.Get ContactGET /integrate/contact/{email}Fetches contact details (ID, Name, Company) from HubSpot using the email address.Create TicketPOST /integrate/ticketCreates a ticket in HubSpot and automatically associates it with the correct Contact ID.Update TicketPATCH /integrate/ticket/{id}Updates ticket status, priority, or description in HubSpot when changed in the local app.Testing the Sync ManuallyYou can test the synchronization without the main app by using curl or Postman:Example: Sync a New TicketBashcurl -X 'POST' \
  'http://localhost:8000/integrate/ticket' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "Login Issue",
  "description": "User cannot reset password",
  "priority": "HIGH",
  "email": "customer@example.com"
}'
Expected Output:JSON{
  "hubspot_ticket_id": "123456789",
  "status": "created",
  "link": "https://app.hubspot.com/contacts/..."
}
📂 Project StructureCRM-integration/
├── main.py              # Entry point for FastAPI application
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (GitIgnored)
└── routes/
    ├── contacts.py      # Endpoints for syncing Customer data
    └── tickets.py       # Endpoints for syncing Support Tickets
🛠️ Key FunctionalitiesContact Resolution: Automatically checks if a contact exists in HubSpot before creating a ticket. If not, it creates the contact first.Ticket Association: Links every support ticket to the correct customer record in HubSpot, maintaining a clean history of interactions.Real-time Updates: Changes made to ticket status or priority are pushed immediately to HubSpot via the PATCH endpoint.Error Handling: Gracefully handles API rate limits and "Contact Not Found" errors, returning meaningful messages to the client.📝 LicenseThis project is for educational purposes as part of a Python Flask/FastAPI training tutorial.
