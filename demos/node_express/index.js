import express from "express";
const app = express();
app.get("/ping", (req, res) => res.json({ ok: true }));
app.listen(3000);
