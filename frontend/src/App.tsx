import ContractGenerator from "./components/ContractGenerator";
import Header from "./components/Header";
import Footer from "./components/Footer";

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              AI Contract Generator
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Generate professional legal contracts in minutes. Simply describe
              your business and let our AI create comprehensive,
              legally-structured documents.
            </p>
          </div>

          <ContractGenerator />
        </div>
      </main>
      <Footer />
    </div>
  );
}

export default App;
