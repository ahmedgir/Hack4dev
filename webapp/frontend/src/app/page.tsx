import Link from "next/link";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { featuredSystem } from "@/data/systems";

const totalFrames = featuredSystem.sessions.reduce((sum, session) => sum + session.totalFrames, 0);
const acceptedFrames = featuredSystem.sessions.reduce((sum, session) => sum + session.acceptedFrames, 0);

export default function Home() {
  return (
    <main>
      <SiteHeader />

      <section className="hero" id="top">
        <img src="/media/systems/corot-2/2026-08-09/hero-field.png" alt="Real stellar field from the CoRoT-2 observing session" />
        <div className="hero-overlay" />
        <div className="hero-inner">
          <p className="breadcrumb">HOME / DISCOVERY TOOL / TRANSIT EXPLORER</p>
          <div className="hero-copy">
            <p className="eyebrow">REAL TELESCOPE DATA · 173 FITS FRAMES · TWO NIGHTS</p>
            <h1>Exoplanet<br />Transit Explorer</h1>
            <p>An evidence-first journey from raw telescope images to a measurable dip in the light of a distant star.</p>
            <div className="hero-actions">
              <Link className="nasa-button" href="/explorer">Explore the observation <span aria-hidden="true">→</span></Link>
              <Link className="text-link light" href="/methodology">Read the methodology</Link>
            </div>
          </div>
        </div>
      </section>

      <section className="overview">
        <article className="overview-copy">
          <p className="section-label">THE QUESTION</p>
          <h2>How do we see a planet that is not visible in the image?</h2>
          <p className="lead">We do not photograph the planet itself. We locate its host star and measure that star&apos;s brightness across a sequence of telescope images.</p>
          <p>When the planet crosses in front of the star, it blocks a small fraction of the light. We compare that signal with reference stars and with published timing, depth, and duration values before stating what the observation can support.</p>
        </article>

        <aside className="featured-record">
          <p className="section-label">FEATURED OBSERVATION</p>
          <h3>{featuredSystem.planetName}</h3>
          <p>{featuredSystem.shortDescription} The recovery now includes two observing nights and an EXOTIC cross-check.</p>
          <dl>
            <div><dt>Orbital period</dt><dd>{featuredSystem.periodDays.toFixed(2)} days</dd></div>
            <div><dt>Published depth</dt><dd>{featuredSystem.publishedDepthPercent}%</dd></div>
            <div><dt>Accepted frames</dt><dd>{acceptedFrames} / {totalFrames}</dd></div>
          </dl>
          <Link href="/explorer" className="nasa-button">Open the observing session <span aria-hidden="true">→</span></Link>
        </aside>
      </section>

      <section className="method">
        <div className="method-heading">
          <p className="section-label">FROM FITS TO EVIDENCE</p>
          <h2>Four inspectable steps—not a black box.</h2>
        </div>
        <ol className="method-list">
          <li><span>01</span><div><h3>Locate the sky</h3><p>Plate solving and WCS map celestial coordinates to exact image pixels.</p></div></li>
          <li><span>02</span><div><h3>Measure light</h3><p>We estimate the background and measure the target in every usable frame.</p></div></li>
          <li><span>03</span><div><h3>Compare stars</h3><p>Gaia reference stars help remove brightness changes shared by the whole field.</p></div></li>
          <li><span>04</span><div><h3>Test the claim</h3><p>Coverage, precision, depth, duration, and timing are checked against published values.</p></div></li>
        </ol>
        <div className="section-action"><Link className="text-link" href="/methodology">See every tool and its role →</Link></div>
      </section>

      <section className="verdict">
        <div className="verdict-copy">
          <p className="section-label">SCIENTIFIC RESULT</p>
          <h2>A promising preliminary recovery of a known transit.</h2>
          <p>The measured signal is broadly compatible in depth and timing. It is not a new discovery and not an independent confirmation. That distinction is part of the result, not hidden in a footnote.</p>
        </div>
        <div className="result-numbers">
          <div><span>MEASURED DEPTH</span><strong>3.18%</strong></div>
          <div><span>PUBLISHED DEPTH</span><strong>2.75%</strong></div>
          <div><span>ACCEPTED FRAMES</span><strong>73 / 87</strong></div>
        </div>
      </section>

      <SiteFooter />
    </main>
  );
}
