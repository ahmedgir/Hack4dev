import type { Metadata } from "next";
import "./globals.css";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL
  ?? (process.env.VERCEL_PROJECT_PRODUCTION_URL
    ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}`
    : "http://localhost:3000");

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "Exoplanet Data Portal | Hack4Dev",
    template: "%s | Exoplanet Data Portal",
  },
  description:
    "An evidence-first journey from raw FITS images to an inspectable exoplanet transit signal.",
  openGraph: {
    type: "website",
    title: "Exoplanet Data Portal",
    description: "From FITS frames to traceable transit evidence.",
    images: [{ url: "/og.png", width: 1733, height: 907, alt: "Exoplanet Data Portal" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Exoplanet Data Portal",
    description: "From FITS frames to traceable transit evidence.",
    images: ["/og.png"],
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" dir="ltr">
      <body>{children}</body>
    </html>
  );
}
