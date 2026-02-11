import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
    title: "VidBrain AI - Intelligent Video Analysis",
    description: "Extract structured insights from any YouTube video using AI",
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <body>{children}</body>
        </html>
    );
}
