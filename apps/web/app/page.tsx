import Link from 'next/link';

export default function HomePage() {
  return (
    <main className="container">
      <section className="card" style={{ padding: '2rem' }}>
        <h1>Build production-ready backend APIs faster</h1>
        <p>
          Submit a product prompt and get a structured implementation workflow with stored artifacts.
          This MVP is designed to evolve into a full autonomous planner/coder/tester/reviewer pipeline.
        </p>
        <Link href="/dashboard">Go to Dashboard →</Link>
      </section>
    </main>
  );
}
