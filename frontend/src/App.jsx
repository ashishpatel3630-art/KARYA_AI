import { useState } from "react";

import Landing from "./pages/landing";
import KaryaLoader from "./components/loading/KaryaLoading";

function App() {
  const [page, setPage] = useState("loading");

  return (
    <>
      {page === "loading" && (
        <KaryaLoader onComplete={() => setPage("landing")} />
      )}

      {page === "landing" && <Landing />}
    </>
  );
}

export default App;