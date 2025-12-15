export default function SettingsPage() {
    return (
      <div className="p-10">
        <h1 className="text-3xl font-bold mb-2">Settings</h1>
        <p className="text-gray-600 mb-10">
          Manage your account, workspace, preferences, and security settings.
        </p>
  
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl">
          <div className="p-6 border rounded-lg bg-white hover:shadow-md transition-shadow">
            <h2 className="text-xl font-semibold mb-2">Account</h2>
            <p className="text-gray-600 text-sm">Update your profile details.</p>
          </div>
  
          <div className="p-6 border rounded-lg bg-white hover:shadow-md transition-shadow">
            <h2 className="text-xl font-semibold mb-2">Preferences</h2>
            <p className="text-gray-600 text-sm">Customize your personal workspace.</p>
          </div>
  
          <div className="p-6 border rounded-lg bg-white hover:shadow-md transition-shadow">
            <h2 className="text-xl font-semibold mb-2">Security</h2>
            <p className="text-gray-600 text-sm">Manage passwords, sessions, and 2FA.</p>
          </div>
  
          <div className="p-6 border rounded-lg bg-white hover:shadow-md transition-shadow">
            <h2 className="text-xl font-semibold mb-2">Billing</h2>
            <p className="text-gray-600 text-sm">View plans, invoices, and payment settings.</p>
          </div>
        </div>
      </div>
    );
  }