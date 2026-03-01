import { JetBrains_Mono } from "next/font/google";

const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
});

export default function TradingLayout({ children }: { children: React.ReactNode }) {
  return <div className={`${jetbrains.variable} font-mono`} style={{ fontFamily: "var(--font-jetbrains), ui-monospace, monospace" }}>{children}</div>;
}
