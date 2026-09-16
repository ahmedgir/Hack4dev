"use client";

import { useEffect, useMemo, useState } from "react";
import type { SessionRecord } from "@/data/systems";

type LightPoint = {
  frame_index: number;
  file_name: string;
  hours_from_expected_mid: number;
  detrended_flux: number;
  transit_model: number;
  accepted: boolean;
  rejection_reason: string;
  target_snr: number;
  background_rms: number;
  registration_stars: number;
};

const WIDTH = 760;
const HEIGHT = 280;
const PAD = { top: 24, right: 22, bottom: 38, left: 54 };

function statusLabel(accepted: boolean) {
  return accepted ? "Accepted measurement" : "Rejected frame";
}

export function TransitExplorer({ session }: { session: SessionRecord }) {
  const [points, setPoints] = useState<LightPoint[]>([]);
  const [activeIndex, setActiveIndex] = useState(session.referenceFrameIndex ?? Math.floor(session.totalFrames / 2));
  const [loadError, setLoadError] = useState(false);

  useEffect(() => {
    fetch(session.lightCurvePath)
      .then((response) => {
        if (!response.ok) throw new Error("Could not load light curve");
        return response.json();
      })
      .then((data: LightPoint[]) => setPoints(data))
      .catch(() => setLoadError(true));
  }, [session.lightCurvePath]);

  const chart = useMemo(() => {
    if (!points.length) return null;
    const accepted = points.filter(
      (point) => point.accepted && point.detrended_flux > 0.88 && point.detrended_flux < 1.12,
    );
    const minX = Math.min(...points.map((point) => point.hours_from_expected_mid));
    const maxX = Math.max(...points.map((point) => point.hours_from_expected_mid));
    const minY = 0.9;
    const maxY = 1.06;
    const x = (value: number) =>
      PAD.left + ((value - minX) / (maxX - minX)) * (WIDTH - PAD.left - PAD.right);
    const y = (value: number) =>
      PAD.top + ((maxY - value) / (maxY - minY)) * (HEIGHT - PAD.top - PAD.bottom);
    const modelPath = points
      .map((point, index) => `${index ? "L" : "M"}${x(point.hours_from_expected_mid)},${y(point.transit_model)}`)
      .join(" ");
    return { accepted, x, y, modelPath };
  }, [points]);

  const active = points[activeIndex];
  const activeImagePath = session.timelineFramesPath
    ? `${session.timelineFramesPath}/${String(activeIndex).padStart(4, "0")}.webp`
    : session.fieldImagePath;

  return (
    <section className="explorer" id="explorer" aria-labelledby="explorer-title">
      <div className="section-kicker">LIVE EVIDENCE / 01</div>
      <div className="section-heading-row">
        <div>
          <h2 id="explorer-title">Follow the light, frame by frame.</h2>
          <p>Every point is a measurement from a real telescope image. Move through the timeline to inspect its context.</p>
        </div>
        <div className="session-stamp">CoRoT-2 · {session.date}</div>
      </div>

      <div className="explorer-grid">
        <div className="field-panel">
          <div className="panel-label-row">
            <span>REFERENCE FIELD</span>
            <span className={active?.accepted === false ? "state rejected" : "state accepted"}>
              {active ? statusLabel(active.accepted) : loadError ? "Data unavailable" : "Loading data"}
            </span>
          </div>
          <div className="field-image-wrap">
            {activeImagePath ? (
              <img
                src={activeImagePath}
                alt={session.timelineFramesPath
                  ? `Observation frame ${activeIndex + 1}`
                  : "CoRoT-2 field with the host and Gaia comparison stars marked"}
              />
            ) : (
              <div className="missing-asset">No field image is available for this session.</div>
            )}
          </div>
          <div className="frame-readout" dir="ltr">
            <span>FRAME {String(activeIndex + 1).padStart(2, "0")} / {session.totalFrames}</span>
            <span>{active?.file_name ?? "Loading measurements…"}</span>
          </div>
        </div>

        <div className="evidence-panel">
          <div className="panel-label-row">
            <span>RELATIVE BRIGHTNESS</span>
            <span>EXPECTED MID = 0h</span>
          </div>
          <div className="chart-wrap" dir="ltr">
            {chart ? (
              <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} role="img" aria-label="Relative stellar brightness across the expected transit window">
                {[0.92, 0.96, 1, 1.04].map((tick) => (
                  <g key={tick}>
                    <line x1={PAD.left} x2={WIDTH - PAD.right} y1={chart.y(tick)} y2={chart.y(tick)} className="grid-line" />
                    <text x={PAD.left - 10} y={chart.y(tick) + 4} className="axis-label" textAnchor="end">{tick.toFixed(2)}</text>
                  </g>
                ))}
                <line x1={chart.x(0)} x2={chart.x(0)} y1={PAD.top} y2={HEIGHT - PAD.bottom} className="mid-line" />
                <path d={chart.modelPath} className="model-line" />
                {chart.accepted.map((point) => (
                  <circle
                    key={point.frame_index}
                    cx={chart.x(point.hours_from_expected_mid)}
                    cy={chart.y(point.detrended_flux)}
                    r={point.frame_index === activeIndex ? 6 : 3}
                    className={point.frame_index === activeIndex ? "data-point active" : "data-point"}
                    onClick={() => setActiveIndex(point.frame_index)}
                  />
                ))}
                <text x={WIDTH / 2} y={HEIGHT - 8} className="axis-title" textAnchor="middle">Hours from expected transit midpoint</text>
                <text x={15} y={HEIGHT / 2} className="axis-title" textAnchor="middle" transform={`rotate(-90 15 ${HEIGHT / 2})`}>Relative flux</text>
              </svg>
            ) : (
              <div className="chart-loading">{loadError ? "The measurements could not be loaded." : "Loading measurements…"}</div>
            )}
          </div>

          <label className="timeline-label" htmlFor="frame-slider">
            <span>OBSERVATION TIMELINE</span>
            <span>{active?.hours_from_expected_mid.toFixed(2) ?? "—"} h</span>
          </label>
          <input
            id="frame-slider"
            className="timeline"
            type="range"
            min="0"
            max={Math.max(0, session.totalFrames - 1)}
            value={activeIndex}
            onChange={(event) => setActiveIndex(Number(event.target.value))}
            aria-label="Select observation frame"
          />

          <div className="metrics-strip">
            <div><span>FLUX</span><strong>{active?.accepted ? active.detrended_flux.toFixed(4) : "—"}</strong></div>
            <div><span>TARGET SNR</span><strong>{active ? active.target_snr.toFixed(1) : "—"}</strong></div>
            <div><span>REFERENCE STARS</span><strong>{active?.registration_stars ?? "—"}</strong></div>
          </div>
          {active && !active.accepted && (
            <p className="rejection-note">Rejection reason: {active.rejection_reason.replaceAll(";", " · ")}</p>
          )}
        </div>
      </div>
    </section>
  );
}
