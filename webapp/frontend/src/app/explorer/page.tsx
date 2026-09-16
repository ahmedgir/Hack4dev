import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { SystemExplorer } from "@/components/SystemExplorer";
import { featuredSystem } from "@/data/systems";

export const metadata: Metadata = {
  title: "Explore CoRoT-2 b",
  description: "Inspect the measured light curve, source field, frame quality, and scientific interpretation for CoRoT-2 b.",
  openGraph: {
    title: "Explore CoRoT-2 b",
    description: "Inspect 173 real FITS frames across two nights and the recovered transit signal.",
    images: [{ url: "/media/systems/corot-2/2026-08-09/hero-field.png", alt: "Stellar field around CoRoT-2" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Explore CoRoT-2 b",
    description: "Inspect 173 real FITS frames across two nights and the recovered transit signal.",
    images: ["/media/systems/corot-2/2026-08-09/hero-field.png"],
  },
};

export default function ExplorerPage() {
  return (
    <main>
      <SiteHeader />
      <section className="page-hero page-hero-image">
        <img src="/media/systems/corot-2/2026-08-09/hero-field.png" alt="Stellar field around CoRoT-2" />
        <div className="hero-overlay" />
        <div className="page-hero-inner">
          <p className="breadcrumb">HOME / DATA / COROT-2 B</p>
          <p className="eyebrow">TWO OBSERVING NIGHTS · AUGUST 2026</p>
          <h1>Inspect the evidence.</h1>
          <p>Move through 173 real FITS exposures and connect each photometric measurement to its source image.</p>
        </div>
      </section>

      <SystemExplorer sessions={featuredSystem.sessions} />

      <section className="validation-section">
        <div className="validation-heading">
          <div><p className="section-label">INDEPENDENT SOFTWARE CROSS-CHECK</p><h2>EXOTIC recovered the signal on both nights.</h2></div>
          <p>EXOTIC 4.3.1 independently repeated alignment, photometry, comparison-star selection, and transit modeling on the same raw images. This strengthens confidence in the calculation, but it is not an independent observation.</p>
        </div>
        <div className="validation-grid">
          <figure>
            <img src="/media/exotic-validation/corot-2-2026-08-09.png" alt="EXOTIC light curve fit for CoRoT-2 b on 9 August 2026" />
            <figcaption><strong>09 August 2026</strong><span>Depth 2.38 ± 0.45% · residual scatter 1.51%</span></figcaption>
          </figure>
          <figure>
            <img src="/media/exotic-validation/corot-2-2026-08-16.png" alt="EXOTIC light curve fit for CoRoT-2 b on 16 August 2026" />
            <figcaption><strong>16 August 2026</strong><span>Depth 2.65 ± 0.35% · residual scatter 1.43%</span></figcaption>
          </figure>
        </div>
      </section>

      <section className="verdict">
        <div className="verdict-copy">
          <p className="section-label">INTERPRETATION</p>
          <h2>What these sessions support—and what they do not.</h2>
          <p>Both nights recover a dip compatible with the published transit. The project pipeline and EXOTIC agree within uncertainty, supporting a promising preliminary recovery—not a new planetary discovery or an independent astronomical confirmation.</p>
          <Link className="text-link light" href="/methodology">Audit the analysis method →</Link>
        </div>
        <div className="result-numbers">
          <div><span>PIPELINE DEPTHS</span><strong>3.18 / 2.88%</strong></div>
          <div><span>EXOTIC DEPTHS</span><strong>2.38 / 2.65%</strong></div>
          <div><span>ACCEPTED FRAMES</span><strong>158 / 173</strong></div>
        </div>
      </section>
      <SiteFooter />
    </main>
  );
}
