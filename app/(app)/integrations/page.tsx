export default function IntegrationsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200">
        <div className="px-8 py-6">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">Integrations</h1>
            <p className="text-sm text-gray-500 mt-1">
              Connect OMI Workspace with the tools your business already uses
            </p>
          </div>
        </div>
      </div>

      <div className="px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl">
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 hover:shadow-md transition-shadow">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Google Drive</h2>
            <p className="text-sm text-gray-600 mb-6">
              Sync documents, contracts, and files.
            </p>
            <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md shadow-sm transition-colors">
              Connect
            </button>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6 hover:shadow-md transition-shadow">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">QuickBooks</h2>
            <p className="text-sm text-gray-600 mb-6">
              Sync invoices, clients, and payment records.
            </p>
            <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md shadow-sm transition-colors">
              Connect
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}