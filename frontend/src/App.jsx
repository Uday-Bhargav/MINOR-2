import { NavLink, Route, Routes } from "react-router-dom";
import { Activity, Bot, Clock3, History, LayoutDashboard, Search } from "lucide-react";

import Chat from "./pages/Chat.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import EventDetail from "./pages/EventDetail.jsx";
import HistoryPage from "./pages/HistoryPage.jsx";
import SearchPage from "./pages/SearchPage.jsx";

export default function App() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <Activity size={26} aria-hidden="true" />
          <div>
            <strong>CrisisIntel</strong>
            <span>Market impact desk</span>
          </div>
        </div>
        <nav className="nav-links" aria-label="Primary navigation">
          <NavItem to="/" icon={<LayoutDashboard size={18} />} label="Dashboard" end />
          <NavItem to="/search" icon={<Search size={18} />} label="Search" />
          <NavItem to="/chat" icon={<Bot size={18} />} label="Chat" />
          <NavItem to="/history" icon={<History size={18} />} label="History" />
        </nav>
        <div className="refresh-note">
          <Clock3 size={16} aria-hidden="true" />
          <span>Refreshes every 15 min</span>
        </div>
      </aside>

      <main className="main-panel">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/events/:id" element={<EventDetail />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/history" element={<HistoryPage />} />
        </Routes>
      </main>
    </div>
  );
}

function NavItem({ to, icon, label, end = false }) {
  return (
    <NavLink to={to} end={end} className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}>
      {icon}
      <span>{label}</span>
    </NavLink>
  );
}

