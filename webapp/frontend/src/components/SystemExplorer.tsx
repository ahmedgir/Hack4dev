"use client";

import { useState } from "react";
import { TransitExplorer } from "@/components/TransitExplorer";
import type { SessionRecord } from "@/data/systems";

export function SystemExplorer({ sessions, starName }: { sessions: SessionRecord[]; starName: string }) {
  const [selected, setSelected] = useState(0);
  const session = sessions[selected];

  return (
    <>
      <div className="session-switcher">
        <div>
          <p className="section-label">OBSERVING NIGHTS</p>
          <h2>{sessions.length > 1 ? `${sessions.length} observing sessions.` : "One reviewed observing session."}</h2>
        </div>
        <div className="session-tabs" role="tablist" aria-label="Choose observing night">
          {sessions.map((item, index) => (
            <button
              key={item.id}
              type="button"
              role="tab"
              aria-selected={selected === index}
              className={selected === index ? "active" : ""}
              onClick={() => setSelected(index)}
            >
              {item.date}
              <span>{item.acceptedFrames}/{item.totalFrames} frames</span>
            </button>
          ))}
        </div>
      </div>
      <TransitExplorer key={session.id} session={session} starName={starName} />
    </>
  );
}
