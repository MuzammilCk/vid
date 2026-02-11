export default function Home() {
    return (
        <main className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900">
            <div className="container mx-auto px-4 py-16">
                <div className="text-center mb-12">
                    <h1 className="text-6xl font-bold text-white mb-4">
                        🧠 VidBrain AI
                    </h1>
                    <p className="text-xl text-gray-300">
                        Extract insights from YouTube videos
                    </p>
                </div>

                <div className="max-w-2xl mx-auto bg-white/10 backdrop-blur-lg rounded-2xl p-8 shadow-2xl">
                    <div className="mb-6">
                        <label className="block text-white text-sm font-medium mb-2">
                            YouTube URL
                        </label>
                        <input
                            type="text"
                            placeholder="https://www.youtube.com/watch?v=..."
                            className="w-full px-4 py-3 rounded-lg bg-white/20 border border-white/30 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
                        />
                    </div>

                    <button className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all duration-200 shadow-lg">
                        Analyze
                    </button>
                </div>
            </div>
        </main>
    );
}
