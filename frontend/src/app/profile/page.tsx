import type { Metadata } from "next";
import { ProfilePage } from "@/features/auth/ProfilePage";

export const metadata: Metadata = { title: "Profile" };

export default function Profile() {
  return <ProfilePage />;
}
