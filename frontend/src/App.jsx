import Header from "./components/layout/Header";
import PageContainer from "./components/layout/PageContainer";
import Dashboard from "./pages/Dashboard";

function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <Header />

      <PageContainer>
        <Dashboard />
      </PageContainer>
    </div>
  );
}

export default App;