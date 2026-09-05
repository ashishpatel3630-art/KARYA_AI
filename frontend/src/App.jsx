import { useState } from "react";

import Landing from "./pages/landing";
import Login from "./pages/Login";
import Desktop from "./pages/Desktop";
import KaryaLoader from "./components/loading/KaryaLoading";

function App() {
  const [page, setPage] = useState("loading");

  return (
    <>
      {page === "loading" && (
        <KaryaLoader onComplete={() => setPage("landing")} />
      )}

      {page === "landing" && <Landing onStart={() => setPage("login")} />}
      {page === "login" && <Login onLogin={() => setPage("desktop")} />}
      {page === "desktop" && <Desktop />}
    </>
  );
}

export default App;