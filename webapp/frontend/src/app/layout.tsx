import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Beyond the Pixel | Hack4Dev",
  description:
    "رحلة تفاعلية من صور FITS الخام إلى دليل قابل للفحص لعبور كوكب معروف.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ar" dir="rtl">
      <body>{children}</body>
    </html>
  );
}
