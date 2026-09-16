import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";

export const metadata: Metadata = {
  title: "Methodology",
  description: "A transparent account of the Python tools, processing stages, outputs, and limits behind the transit analysis.",
};

const tools = [
  { name: "Astropy", tag: "FITS · WCS · TIME", purpose: "Reads the original FITS images, interprets World Coordinate System headers, converts sky coordinates to pixels, and handles observation time in astronomical standards.", output: "Calibrated image arrays, target coordinates, and BJD timestamps." },
  { name: "Astroalign + Gaia", tag: "CONSTRAINED SKY MATCH", purpose: "Matches stars detected in the reference exposure to Gaia DR3 around the known host coordinate. Scale, rotation, residual error, and the presence of a detected star at the predicted target position must all pass before the WCS is accepted.", output: "A solved WCS header plus match-count and residual diagnostics." },
  { name: "ASTAP + Astrometry.net", tag: "PLATE-SOLVE FALLBACK", purpose: "Cached Astrometry.net solutions remain the reference baseline and the online service is a fallback for a field that the constrained Gaia matcher cannot solve. ASTAP was attempted on 18 uncached sessions and solved none of these undersampled images.", output: "A fallback WCS when a solver genuinely succeeds; failed attempts remain documented." },
  { name: "Astroquery", tag: "REFERENCE CATALOG", purpose: "Queries Gaia for suitable stars in the same field so atmospheric and instrumental changes can be measured against stable references.", output: "Coordinates and identifiers for the comparison-star ensemble." },
  { name: "SEP", tag: "SOURCE EXTRACTION", purpose: "Estimates the sky background and detects compact light sources. Subtracting the background prevents sky glow from being counted as stellar flux.", output: "Background-subtracted frames and detected source candidates." },
  { name: "NumPy", tag: "NUMERICAL CORE", purpose: "Carries the image arrays and performs robust numerical operations throughout calibration, registration, photometry, and quality control.", output: "Fast, reproducible numerical measurements for every frame." },
  { name: "SciPy", tag: "FILTERING · FITTING", purpose: "Applies controlled image filters and fits a simple trapezoid transit model with least-squares optimization.", output: "Frame alignment support and fitted transit parameters." },
  { name: "Pandas", tag: "TABLES · QUALITY CONTROL", purpose: "Collects timestamps, flux, signal-to-noise, registration quality, acceptance flags, and rejection reasons into auditable tables.", output: "Machine-readable per-frame measurements and summaries." },
  { name: "Matplotlib", tag: "SCIENTIFIC OUTPUT", purpose: "Renders the verification field and diagnostic light-curve figures used during analysis and review.", output: "Static scientific figures that can be checked outside the website." },
  { name: "EXOTIC 4.3.1", tag: "CROSS-VALIDATION", purpose: "Repeats alignment, PSF photometry, comparison-star selection, and transit fitting through an established independent software path using the same raw images.", output: "A second set of transit depths, timings, uncertainties, and residual diagnostics for both nights." },
];

export default function MethodologyPage() {
  return (
    <main>
      <SiteHeader />
      <section className="page-hero">
        <div className="page-hero-inner">
          <p className="breadcrumb">HOME / METHODOLOGY</p>
          <p className="eyebrow">OPEN PIPELINE</p>
          <h1>Every tool has a defined job.</h1>
          <p>This page describes what the current Python pipeline actually uses, what each stage produces, and where interpretation still requires caution.</p>
        </div>
      </section>

      <section className="content-shell methodology-intro">
        <div>
          <p className="section-label">ANALYSIS CHAIN</p>
          <h2>From detector counts to a transit-shaped signal.</h2>
        </div>
        <p>Each stage leaves an intermediate result that can be inspected: calibrated arrays, a solved sky map, reference stars, frame-level flux measurements, quality flags, and a final model comparison. The website presents those outputs; it does not replace the scientific pipeline.</p>
      </section>

      <section className="tool-section">
        <div className="tool-grid">
          {tools.map((tool, index) => (
            <article className="tool-card" key={tool.name}>
              <div className="tool-index">{String(index + 1).padStart(2, "0")}</div>
              <p className="tool-tag">{tool.tag}</p>
              <h2>{tool.name}</h2>
              <p>{tool.purpose}</p>
              <div className="tool-output"><strong>Produces</strong><span>{tool.output}</span></div>
            </article>
          ))}
        </div>
      </section>

      <section className="transparency-band">
        <div>
          <p className="section-label">TRANSPARENCY NOTE</p>
          <h2>Installed does not mean used.</h2>
        </div>
        <div>
          <p>The project environment also contains Photutils and Plotly. They remain available for future pipeline work, but the current proof-of-concept path does not call them, so we do not credit them as part of this result.</p>
          <p>EXOTIC is used as a separate validation path, not as a hidden stage inside the project pipeline. It analyzes the same observations, so this is an independent software check—not an independent astronomical observation.</p>
          <p>The Gaia matcher was regression-tested against all seven cached reference solutions: target-position error ranged from 0.075 to 0.421 pixel. This removes the Astrometry.net queue from the normal path without accepting an unverified approximate coordinate.</p>
        </div>
      </section>

      <section className="page-cta">
        <div><p className="section-label">SEE THE OUTPUT</p><h2>Now inspect the observation itself.</h2></div>
        <Link className="nasa-button" href="/systems/corot-2">Open CoRoT-2 b <span aria-hidden="true">→</span></Link>
      </section>
      <SiteFooter />
    </main>
  );
}
