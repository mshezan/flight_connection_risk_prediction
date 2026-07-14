import Header from "@/components/layout/Header";
import SearchPanel from "@/components/search/SearchPanel";

function App() {
  return (
    <main className="min-h-screen bg-[#07101f] text-white">
      <div className="mx-auto max-w-[1500px] px-4 py-4">
        <div className="rounded-[20px] border border-[#26344a] bg-[#0a1425] shadow-2xl shadow-black/20">
          <Header />

          <section className="px-6 pb-6 lg:px-9">
            <SearchPanel />
          </section>
        </div>
      </div>
    </main>
  );
}

export default App;