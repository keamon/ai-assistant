import { useEffect, useState } from "react";
import type { Room, RoomAssignment } from "../types";
import { api } from "../api";
import Modal from "./Modal";

export interface ScheduleInitial {
  title: string;
  attendees: string[];
  date: string;
  start_time: string;
  end_time: string;
}

export default function ScheduleModal({
  initial,
  onClose,
  onScheduled,
}: {
  initial: ScheduleInitial;
  onClose: () => void;
  onScheduled: () => void;
}) {
  const [title, setTitle] = useState(initial.title);
  const [attendeesText, setAttendeesText] = useState(initial.attendees.join(", "));
  const [date, setDate] = useState(initial.date);
  const [start, setStart] = useState(initial.start_time);
  const [end, setEnd] = useState(initial.end_time);
  const [room, setRoom] = useState<RoomAssignment | null>(null);
  const [availableRooms, setAvailableRooms] = useState<Room[]>([]);
  const [selectedRoomId, setSelectedRoomId] = useState("");
  const [roomLoading, setRoomLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  const attendees = () => attendeesText.split(",").map((a) => a.trim()).filter(Boolean);

  // Preview the suggested room + list every free room whenever attendees / date / time change.
  useEffect(() => {
    let cancelled = false;
    setRoomLoading(true);
    const win = { attendees: attendees(), date, start_time: start, end_time: end };
    Promise.all([api.assignRoom(win), api.availableRooms(win)])
      .then(([assign, avail]) => {
        if (cancelled) return;
        setRoom(assign);
        setAvailableRooms(avail.available_rooms);
        setSelectedRoomId((prev) =>
          prev && avail.available_rooms.some((r) => r.id === prev) ? prev : assign.assigned?.id ?? ""
        );
      })
      .catch(() => {
        if (cancelled) return;
        setRoom(null);
        setAvailableRooms([]);
        setSelectedRoomId("");
      })
      .finally(() => !cancelled && setRoomLoading(false));
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [attendeesText, date, start, end]);

  const confirm = async () => {
    setSaving(true);
    try {
      await api.schedule({
        title,
        attendees: attendees(),
        date,
        start_time: start,
        end_time: end,
        room_id: selectedRoomId || undefined,
      });
      onScheduled();
      onClose();
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal title="Schedule meeting" onClose={onClose} width={600}>
      <div className="form">
        <label className="field">
          <span>Title</span>
          <input value={title} onChange={(e) => setTitle(e.target.value)} />
        </label>

        <label className="field">
          <span>Attendees</span>
          <input
            value={attendeesText}
            onChange={(e) => setAttendeesText(e.target.value)}
            placeholder="comma-separated emails"
          />
        </label>

        <div className="field-row">
          <label className="field">
            <span>Date</span>
            <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
          </label>
          <label className="field">
            <span>Start</span>
            <input type="time" value={start} onChange={(e) => setStart(e.target.value)} />
          </label>
          <label className="field">
            <span>End</span>
            <input type="time" value={end} onChange={(e) => setEnd(e.target.value)} />
          </label>
        </div>

        <div className="room-suggest">
          <span className="section-title" style={{ marginBottom: 6 }}>Meeting room</span>
          {roomLoading && <div className="small muted">Finding available rooms…</div>}
          {!roomLoading && availableRooms.length > 0 && (
            <div className="room-pick">
              <select value={selectedRoomId} onChange={(e) => setSelectedRoomId(e.target.value)}>
                {availableRooms.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.name} · {r.building} fl {r.floor} · seats {r.capacity}
                    {r.id === room?.assigned?.id ? " (recommended)" : ""}
                  </option>
                ))}
              </select>
              {room?.rationale && selectedRoomId === room.assigned?.id && (
                <div className="small muted" style={{ marginTop: 6 }}>{room.rationale}</div>
              )}
            </div>
          )}
          {!roomLoading && availableRooms.length === 0 && (
            <div className="small" style={{ color: "var(--amber)" }}>
              No room fits that window — you can still schedule; book a room manually later.
            </div>
          )}
        </div>

        <div className="form-actions">
          <button className="btn-outline" onClick={onClose}>
            Cancel
          </button>
          <button className="btn" onClick={confirm} disabled={saving || !title.trim()}>
            {saving ? "Scheduling…" : "Confirm & add to calendar"}
          </button>
        </div>
      </div>
    </Modal>
  );
}
