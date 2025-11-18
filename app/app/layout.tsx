import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "FF Domination - Your AI Fantasy Football Coach",
  description: "Transform into a league champion with 24/7 AI-powered fantasy football analysis, trade suggestions, and expert draft strategy.",
  keywords: ["fantasy football", "AI", "draft tool", "trade analyzer", "waiver wire"],
  authors: [{ name: "FF Domination" }],
  openGraph: {
    title: "FF Domination - AI Fantasy Football Coach",
    description: "Win your fantasy league with AI-powered insights",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
