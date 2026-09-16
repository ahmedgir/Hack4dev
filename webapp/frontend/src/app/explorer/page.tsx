import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { TransitExplorer } from "@/components/TransitExplorer";
import { featuredSystem } from "@/data/systems";

export const metadata: Metadata = {
  title: "Explore CoRoT-2 b",
  description: "Inspect the measured light curve, source field, frame quality, and scientific interpretation for CoRoT-2 b.",
  openGraph: {
    title: "Explore CoRoT-2 b",
    description: "Inspect 87 real FITS frames and the recovered transit signal.",
    images: [{ url: "/media/systems/corot-2/2026-08-09/hero-field.png", alt: "Stellar field around CoRoT-2" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Explore CoRoT-2 b",
    description: "Inspect 87 real FITS frames and the recovered transit signal.",
    images: ["/media/systems/corot-2/2026-08-09/hero-field.png"],
  },
};

const session = featuredSystem.sessions[0];

export default function ExplorerPage() {
  return (
    <main>
      <SiteHeader />
      <section className="page-hero page-hero-image">
        <img src="/media/systems/corot-2/2026-08-09/hero-field.png" alt="Stellar field around CoRoT-2" />
        <div className="hero-overlay" />
        <div className="page-hero-inner">
          <p className="breadcrumb">HOME / DATA / COROT-2 B</p>
          <p className="eyebrow">OBSERVING SESSION · 2026-08-09</p>
          <h1>Inspect the evidence.</h1>
          <p>Move through 87 real FITS exposures and connect each photometric measurement to its source image.</p>
        </div>
      </section>

      <TransitExplorer session={session} />

      <section className="verdict">
        <div className="verdict-copy">
          <p className="section-label">INTERPRETATION</p>
          <h2>What this session supports—and what it does not.</h2>
          <p>The recovered dip is broadly compatible with the published transit depth and expected timing. The dataset supports a promising preliminary recovery, not a new planetary discovery or an independent confirmation.</p>
          <Link className="text-link light" href="/methodology">Audit the analysis method →</Link>
        </div>
        <div className="result-numbers">
          <div><span>MEASURED DEPTH</span><strong>3.18%</strong></div>
          <div><span>PUBLISHED DEPTH</span><strong>2.75%</strong></div>
          <div><span>ACCEPTED FRAMES</span><strong>{session.acceptedFrames} / {session.totalFrames}</strong></div>
        </div>
      </section>
      <SiteFooter />
    </main>
  );
}
