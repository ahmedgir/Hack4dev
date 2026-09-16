import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { SystemExplorer } from "@/components/SystemExplorer";
import { getSystem, getSystemStatus, statusLabels, systems } from "@/data/systems";

type Props = { params: Promise<{ slug: string }> };

const interpretations = {
  promising_preliminary_transit: {
    title: "A promising preliminary recovery of a known transit.",
    body: "The accepted measurements cover the expected event and the fitted signal is broadly compatible with published parameters. This is not a new discovery or an independent astronomical confirmation.",
  },
  insufficient_for_transit_claim: {
    title: "This observation is not sufficient for a transit claim.",
    body: "Missing baseline, rejected frames, or excessive scatter prevent a defensible recovery. The diagnostic fit remains visible for audit, but its depth must not be interpreted as a measurement of the planet.",
  },
  transit_like_but_parameters_inconsistent: {
    title: "A transit-like shape is not enough.",
    body: "The sequence contains a dip, but its fitted depth or duration disagrees with the published transit. We preserve the result as a useful failure case rather than promoting it to a recovery.",
  },
  not_analysed: {
    title: "No reviewed pipeline result is available yet.",
    body: "The target and published orbital parameters are ready. Evidence panels will appear only after a session completes the same pipeline and review contract used by the other systems.",
  },
};

export const dynamicParams = false;

export function generateStaticParams() {
  return systems.map((system) => ({ slug: system.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const system = getSystem((await params).slug);
  if (!system) return {};
  const image = system.sessions[0]?.fieldImagePath;
  return {
    title: `${system.planetName} evidence`,
    description: system.shortDescription,
    openGraph: { title: `${system.planetName} — Exoplanet Data Portal`, description: system.shortDescription, images: image ? [{ url: image, alt: system.imageLabel }] : [] },
    twitter: { card: "summary_large_image", title: `${system.planetName} — Exoplanet Data Portal`, description: system.shortDescription, images: image ? [image] : [] },
  };
}

export default async function SystemPage({ params }: Props) {
  const system = getSystem((await params).slug);
  if (!system) notFound();
  const status = getSystemStatus(system);
  const interpretation = interpretations[status];
  const totalFrames = system.sessions.reduce((sum, session) => sum + session.totalFrames, 0);
  const acceptedFrames = system.sessions.reduce((sum, session) => sum + session.acceptedFrames, 0);
  const firstSession = system.sessions[0];

  return (
    <main>
      <SiteHeader />
      <section className={`page-hero system-detail-hero ${firstSession ? "page-hero-image" : "system-detail-no-image"}`}>
        {firstSession && <img src={firstSession.fieldImagePath} alt={system.imageLabel} />}
        <div className="hero-overlay" />
        <div className="page-hero-inner">
          <p className="breadcrumb">HOME / SYSTEMS / {system.planetName.toUpperCase()}</p>
          <p className="eyebrow">{system.discoverySurvey} · {statusLabels[status]}</p>
          <h1>{system.planetName}</h1>
          <p>{system.shortDescription}</p>
        </div>
      </section>

      <section className="system-profile">
        <div><p className="section-label">PUBLISHED SYSTEM PROFILE</p><h2>What was known before our observation.</h2><p>These values identify the known system and define the expected signal. They are reference parameters, not results produced by this website.</p></div>
        <dl>
          <div><dt>Host star</dt><dd>{system.starName}</dd></div>
          <div><dt>Orbital period</dt><dd>{system.periodDays} days</dd></div>
          <div><dt>Transit depth</dt><dd>{system.publishedDepthPercent}%</dd></div>
          <div><dt>Transit duration</dt><dd>{system.durationHours} hours</dd></div>
          <div><dt>RA / Dec</dt><dd>{system.raDeg.toFixed(6)}° / {system.decDeg.toFixed(6)}°</dd></div>
          <div><dt>Gaia magnitude</dt><dd>{system.gaiaMagnitude}</dd></div>
        </dl>
      </section>

      {system.sessions.length ? <SystemExplorer sessions={system.sessions} starName={system.starName} /> : (
        <section className="awaiting-evidence"><p className="section-label">EVIDENCE STATUS</p><h2>Awaiting a pipeline-complete session.</h2><p>No light curve, fitted depth, or success claim is shown until real observation products pass the shared data validation contract.</p><Link className="text-link" href="/methodology">Review the required analysis →</Link></section>
      )}

      {system.slug === "corot-2" && (
        <section className="validation-section">
          <div className="validation-heading"><div><p className="section-label">INDEPENDENT SOFTWARE CROSS-CHECK</p><h2>EXOTIC recovered the signal on both nights.</h2></div><p>EXOTIC 4.3.1 repeated alignment, photometry, comparison-star selection, and transit modeling on the same raw images. This strengthens confidence in the calculation, but it is not an independent observation.</p></div>
          <div className="validation-grid">
            <figure><img src="/media/exotic-validation/corot-2-2026-08-09.png" alt="EXOTIC light curve fit for CoRoT-2 b on 9 August 2026" /><figcaption><strong>09 August 2026</strong><span>Depth 2.38 ± 0.45% · residual scatter 1.51%</span></figcaption></figure>
            <figure><img src="/media/exotic-validation/corot-2-2026-08-16.png" alt="EXOTIC light curve fit for CoRoT-2 b on 16 August 2026" /><figcaption><strong>16 August 2026</strong><span>Depth 2.65 ± 0.35% · residual scatter 1.43%</span></figcaption></figure>
          </div>
        </section>
      )}

      <section className="verdict">
        <div className="verdict-copy"><p className="section-label">INTERPRETATION</p><h2>{interpretation.title}</h2><p>{interpretation.body}</p><a className="text-link light" href={system.sourceUrl} target="_blank" rel="noreferrer">Open NASA catalog record ↗</a></div>
        <div className="result-numbers">
          <div><span>REVIEWED SESSIONS</span><strong>{system.sessions.length}</strong></div>
          <div><span>ACCEPTED FRAMES</span><strong>{system.sessions.length ? `${acceptedFrames} / ${totalFrames}` : "—"}</strong></div>
          <div><span>{firstSession?.fitValid ? "MEASURED DEPTH" : "PUBLISHED DEPTH"}</span><strong>{firstSession?.fitValid ? `${firstSession.measuredDepthPercent?.toFixed(2)}%` : `${system.publishedDepthPercent}%`}</strong></div>
        </div>
      </section>
      <SiteFooter />
    </main>
  );
}
