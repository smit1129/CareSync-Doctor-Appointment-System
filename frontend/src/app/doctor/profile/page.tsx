"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { doctorsAPI, DoctorInfo, AvailabilityInfo } from "@/lib/api";

const DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

export default function DoctorProfile() {
  const router = useRouter();
  const { user, token, loading: authLoading, isDoctor } = useAuth();
  
  const [profile, setProfile] = useState<Partial<DoctorInfo>>({});
  const [availabilities, setAvailabilities] = useState<AvailabilityInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [savingProfile, setSavingProfile] = useState(false);
  const [savingAvail, setSavingAvail] = useState(false);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    if (authLoading) return;
    if (!user || !isDoctor) {
      router.push("/auth/login");
      return;
    }
    
    let active = true;
    const fetchProfileData = async () => {
      if (!token || !user?.doctor_id) return;
      setLoading(true);
      try {
        const [docData, availData] = await Promise.all([
          doctorsAPI.getById(user.doctor_id),
          doctorsAPI.getMyAvailability(token),
        ]);
        if (active) {
          setProfile(docData);
          
          const currentAvail = [...availData];
          for (let i = 0; i < 7; i++) {
            if (!currentAvail.find(a => a.day_of_week === i)) {
              currentAvail.push({
                id: `new-${i}`,
                doctor_id: user.doctor_id,
                day_of_week: i,
                start_time: "09:00",
                end_time: "17:00",
                slot_duration_minutes: 30,
                is_active: false
              });
            }
          }
          setAvailabilities(currentAvail.sort((a, b) => a.day_of_week - b.day_of_week));
        }
      } catch {
        if (active) setMsg("Failed to load profile data");
      }
      if (active) setLoading(false);
    };
    
    fetchProfileData();
    return () => { active = false; };
  }, [user, authLoading, isDoctor, router, token]);

  const fetchData = async () => {
    if (!token || !user?.doctor_id) return;
    try {
      const availData = await doctorsAPI.getMyAvailability(token);
      const currentAvail = [...availData];
      for (let i = 0; i < 7; i++) {
        if (!currentAvail.find(a => a.day_of_week === i)) {
          currentAvail.push({
            id: `new-${i}`,
            doctor_id: user.doctor_id,
            day_of_week: i,
            start_time: "09:00",
            end_time: "17:00",
            slot_duration_minutes: 30,
            is_active: false
          });
        }
      }
      setAvailabilities(currentAvail.sort((a, b) => a.day_of_week - b.day_of_week));
    } catch {
      // empty
    }
  };

  const handleProfileSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setSavingProfile(true);
    try {
      await doctorsAPI.updateProfile(token, profile);
      setMsg("Profile updated successfully");
    } catch (err: unknown) {
      setMsg(err instanceof Error ? err.message : "Failed to update profile");
    }
    setSavingProfile(false);
  };

  const handleAvailabilitySave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setSavingAvail(true);
    try {
      const input = availabilities.map(a => ({
        day_of_week: a.day_of_week,
        start_time: a.start_time,
        end_time: a.end_time,
        slot_duration_minutes: a.slot_duration_minutes,
        is_active: a.is_active,
      }));
      await doctorsAPI.updateAvailability(token, input);
      setMsg("Availability schedule updated");
      fetchData(); // reload to get real IDs for new ones
    } catch (err: unknown) {
      setMsg(err instanceof Error ? err.message : "Failed to update schedule");
    }
    setSavingAvail(false);
  };

  const updateAvail = (index: number, field: keyof AvailabilityInfo, value: string | number | boolean) => {
    const newAvail = [...availabilities];
    newAvail[index] = { ...newAvail[index], [field]: value };
    setAvailabilities(newAvail);
  };

  if (authLoading || loading) {
    return <div className="max-w-4xl mx-auto px-4 py-12"><div className="skeleton h-8 w-1/4 mb-8" /><div className="skeleton h-64 mb-8 rounded-xl" /></div>;
  }

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-foreground mb-6">Doctor Profile & Settings</h1>

        {msg && (
          <div className="mb-6 p-4 bg-teal-50/90 dark:bg-teal-950/40 border border-teal-300/80 dark:border-teal-800 text-teal-950 dark:text-teal-200 rounded-xl flex justify-between items-center font-medium shadow-sm">
            <span>{msg}</span>
            <button onClick={() => setMsg("")} className="font-bold ml-4 text-teal-900 dark:text-teal-300 hover:opacity-75">✕</button>
          </div>
        )}

        <div className="bg-surface rounded-2xl shadow-sm border border-border p-6 sm:p-8 mb-8">
          <h2 className="text-xl font-bold text-foreground mb-6">Professional Information</h2>
          <form onSubmit={handleProfileSave} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-foreground mb-1">Phone Number</label>
                <input type="text" value={profile.phone_number || ""} onChange={e => setProfile({...profile, phone_number: e.target.value})} className="w-full px-4 py-2 border border-border bg-surface text-foreground rounded-lg focus:ring-2 focus:ring-accent outline-none" />
              </div>
              <div>
                <label className="block text-sm font-semibold text-foreground mb-1">Specialization</label>
                <input type="text" value={profile.specialization || ""} onChange={e => setProfile({...profile, specialization: e.target.value})} className="w-full px-4 py-2 border border-border bg-surface text-foreground rounded-lg focus:ring-2 focus:ring-accent outline-none" />
              </div>
              <div>
                <label className="block text-sm font-semibold text-foreground mb-1">Qualification</label>
                <input type="text" value={profile.qualification || ""} onChange={e => setProfile({...profile, qualification: e.target.value})} className="w-full px-4 py-2 border border-border bg-surface text-foreground rounded-lg focus:ring-2 focus:ring-accent outline-none" />
              </div>
              <div>
                <label className="block text-sm font-semibold text-foreground mb-1">Experience (Years)</label>
                <input type="number" min="0" value={profile.experience_years || 0} onChange={e => setProfile({...profile, experience_years: parseInt(e.target.value)})} className="w-full px-4 py-2 border border-border bg-surface text-foreground rounded-lg focus:ring-2 focus:ring-accent outline-none" />
              </div>
              <div>
                <label className="block text-sm font-semibold text-foreground mb-1">Consultation Fee (₹)</label>
                <input type="number" min="0" value={profile.consultation_fee || 0} onChange={e => setProfile({...profile, consultation_fee: parseInt(e.target.value)})} className="w-full px-4 py-2 border border-border bg-surface text-foreground rounded-lg focus:ring-2 focus:ring-accent outline-none" />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-semibold text-foreground mb-1">Clinic Address</label>
                <input type="text" value={profile.clinic_address || ""} onChange={e => setProfile({...profile, clinic_address: e.target.value})} className="w-full px-4 py-2 border border-border bg-surface text-foreground rounded-lg focus:ring-2 focus:ring-accent outline-none" />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-semibold text-foreground mb-1">Bio (Optional)</label>
                <textarea rows={3} value={profile.bio || ""} onChange={e => setProfile({...profile, bio: e.target.value})} className="w-full px-4 py-2 border border-border bg-surface text-foreground rounded-lg focus:ring-2 focus:ring-accent outline-none" />
              </div>
            </div>
            <div className="flex justify-end pt-4">
              <button type="submit" disabled={savingProfile} className="px-6 py-2.5 bg-primary text-primary-foreground font-medium rounded-xl hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm">
                {savingProfile ? "Saving..." : "Save Profile"}
              </button>
            </div>
          </form>
        </div>

        <div className="bg-surface rounded-2xl shadow-sm border border-border p-6 sm:p-8">
          <h2 className="text-xl font-bold text-foreground mb-2">Availability Schedule</h2>
          <p className="text-sm text-muted-foreground mb-6">Define your working hours and slot durations.</p>
          
          <form onSubmit={handleAvailabilitySave}>
            <div className="space-y-4">
              {availabilities.map((avail, idx) => (
                <div key={idx} className="flex flex-col md:flex-row md:items-center gap-4 p-4 border border-border rounded-xl hover:bg-surface-subtle transition-colors">
                  <div className="w-32 flex items-center gap-3">
                    <input type="checkbox" checked={avail.is_active} onChange={e => updateAvail(idx, "is_active", e.target.checked)} className="w-5 h-5 text-accent rounded" />
                    <span className="font-semibold text-foreground">{DAY_NAMES[avail.day_of_week]}</span>
                  </div>
                  
                  {avail.is_active ? (
                    <div className="flex-1 grid grid-cols-3 gap-3">
                      <div>
                        <label className="block text-xs font-medium text-muted-foreground mb-1">Start Time</label>
                        <input type="time" value={avail.start_time} onChange={e => updateAvail(idx, "start_time", e.target.value)} className="w-full px-3 py-2 border border-border bg-surface text-foreground rounded-lg text-sm outline-none focus:ring-2 focus:ring-accent" />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-muted-foreground mb-1">End Time</label>
                        <input type="time" value={avail.end_time} onChange={e => updateAvail(idx, "end_time", e.target.value)} className="w-full px-3 py-2 border border-border bg-surface text-foreground rounded-lg text-sm outline-none focus:ring-2 focus:ring-accent" />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-muted-foreground mb-1">Slot Duration (min)</label>
                        <select value={avail.slot_duration_minutes} onChange={e => updateAvail(idx, "slot_duration_minutes", parseInt(e.target.value))} className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-surface text-foreground outline-none focus:ring-2 focus:ring-accent">
                          <option value={15}>15 mins</option>
                          <option value={20}>20 mins</option>
                          <option value={30}>30 mins</option>
                          <option value={45}>45 mins</option>
                          <option value={60}>60 mins</option>
                        </select>
                      </div>
                    </div>
                  ) : (
                    <div className="flex-1 text-muted-foreground text-sm italic font-medium">Not working on this day</div>
                  )}
                </div>
              ))}
            </div>
            <div className="flex justify-end pt-6">
              <button type="submit" disabled={savingAvail} className="px-6 py-2.5 bg-primary text-primary-foreground font-medium rounded-xl hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm">
                {savingAvail ? "Saving..." : "Save Schedule"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
