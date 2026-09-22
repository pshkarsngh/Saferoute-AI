import { useState, type FormEvent } from "react";

interface SearchFormProps {
  onSearch: (
    source: { latitude: number; longitude: number },
    destination: { latitude: number; longitude: number },
  ) => Promise<void>;
  disabled: boolean;
}

/** Client-side validation only (bounds); backend remains authoritative (02_TRD.md §9). */
function validCoord(value: number): boolean {
  return Number.isFinite(value);
}

export function SearchForm({ onSearch, disabled }: SearchFormProps) {
  const [srcLat, setSrcLat] = useState("");
  const [srcLon, setSrcLon] = useState("");
  const [dstLat, setDstLat] = useState("");
  const [dstLon, setDstLon] = useState("");
  const [fieldError, setFieldError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const source = { latitude: Number(srcLat), longitude: Number(srcLon) };
    const destination = { latitude: Number(dstLat), longitude: Number(dstLon) };

    if (!validCoord(source.latitude) || !validCoord(source.longitude)) {
      setFieldError("Please enter a valid source location.");
      return;
    }
    if (!validCoord(destination.latitude) || !validCoord(destination.longitude)) {
      setFieldError("Please enter a valid destination.");
      return;
    }
    setFieldError(null);
    await onSearch(source, destination);
  }

  return (
    <form className="search-form" onSubmit={handleSubmit}>
      <fieldset disabled={disabled}>
        <legend>Source</legend>
        <label>
          Latitude
          <input type="number" step="any" value={srcLat} onChange={(e) => setSrcLat(e.target.value)} placeholder="12.97" />
        </label>
        <label>
          Longitude
          <input type="number" step="any" value={srcLon} onChange={(e) => setSrcLon(e.target.value)} placeholder="74.88" />
        </label>
      </fieldset>

      <fieldset disabled={disabled}>
        <legend>Destination</legend>
        <label>
          Latitude
          <input type="number" step="any" value={dstLat} onChange={(e) => setDstLat(e.target.value)} placeholder="12.91" />
        </label>
        <label>
          Longitude
          <input type="number" step="any" value={dstLon} onChange={(e) => setDstLon(e.target.value)} placeholder="74.85" />
        </label>
      </fieldset>

      {fieldError && <p className="error" role="alert">{fieldError}</p>}

      <button type="submit" disabled={disabled}>
        {disabled ? "Loading…" : "Analyze Routes"}
      </button>
    </form>
  );
}