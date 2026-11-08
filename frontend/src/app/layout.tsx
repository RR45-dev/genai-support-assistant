export const metadata = { title: "Support Assistant" };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ fontFamily: "sans-serif", maxWidth: 700, margin: "40px auto" }}>{children}</body>
    </html>
  );
}
