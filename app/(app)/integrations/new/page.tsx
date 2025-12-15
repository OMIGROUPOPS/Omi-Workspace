export default function NewIntegrationPage() {
    return (
      <div>
        <h1 className="text-xl font-semibold">Add a New Integration</h1>
        <p className="text-gray-600 mt-2">
          Choose a tool to connect with OMI Workspace.
        </p>
  
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
  
          <div className="p-4 border rounded-md bg-white shadow-sm">
            <h2 className="font-medium">Zapier</h2>
            <p className="text-sm text-gray-600 mt-1">
              Automate workflows and connect thousands of apps.
            </p>
            <button className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
              Connect
            </button>
          </div>
  
          <div className="p-4 border rounded-md bg-white shadow-sm">
            <h2 className="font-medium">Make.com</h2>
            <p className="text-sm text-gray-600 mt-1">
              Build powerful automated scenarios with visual tools.
            </p>
            <button className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
              Connect
            </button>
          </div>
  
        </div>
      </div>
    );
  }
  