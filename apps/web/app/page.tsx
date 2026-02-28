export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold mb-8 text-center">
          Buffett Screener
        </h1>
        <p className="text-center text-lg mb-4">
          Value investing stock screener inspired by Warren Buffett principles
        </p>
        <div className="mt-8 grid gap-4 text-center lg:grid-cols-3">
          <div className="rounded-lg border border-gray-300 dark:border-gray-700 p-6">
            <h2 className="text-2xl font-semibold mb-2">Quality Companies</h2>
            <p className="text-sm opacity-75">
              Filter stocks based on fundamental quality metrics
            </p>
          </div>
          <div className="rounded-lg border border-gray-300 dark:border-gray-700 p-6">
            <h2 className="text-2xl font-semibold mb-2">Value Analysis</h2>
            <p className="text-sm opacity-75">
              Identify undervalued opportunities with margin of safety
            </p>
          </div>
          <div className="rounded-lg border border-gray-300 dark:border-gray-700 p-6">
            <h2 className="text-2xl font-semibold mb-2">Long-term Focus</h2>
            <p className="text-sm opacity-75">
              Track companies with sustainable competitive advantages
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}
