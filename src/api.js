import axios from "axios";

const api = axios.create({
    baseURL: "https://medilens-1-fx8f.onrender.com"
});

export default api;