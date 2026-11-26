import type { Stats } from "../types/stats";
import { request } from "./client";

export const fetchStats = () => request<Stats>("/api/stats");
