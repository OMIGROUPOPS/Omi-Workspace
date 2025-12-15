import dynamic from "next/dynamic";

// Load client components WITHOUT forcing the layout to become a client component
const Sidebar = dynamic(() => import("@/components/Sidebar"), { ssr: false });
const Topbar = dynamic(() => import("@/components/Topbar"), { ssr: false });

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Topbar />
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
