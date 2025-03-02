require("dotenv").config();
const express = require("express");
const path = require("path");
const bodyParser = require("body-parser");
const jwt = require("jsonwebtoken"); // Import jsonwebtoken
const cookieParser = require("cookie-parser"); // Import cookie-parser

const app = express();
const PORT = process.env.PORT || 3000;

const users = [];

app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));
app.use("/assets", express.static("assets"));

app.use(bodyParser.urlencoded({ extended: true })); // Middleware to parse form data
app.use(cookieParser()); // Use cookie-parser middleware

// Routes
app.get("/login", (req, res) => {
  res.render("login");
});

app.get("/register", (req, res) => {
  res.render("register");
});

app.post("/api/auth/sign-in", async (req, res) => {
  res.redirect("/dashboard"); // Return success message
});

app.post("/api/auth/sign-up", async (req, res) => {
  res.redirect("/dashboard");
});

app.get("/dashboard", (req, res) => {
  res.render("dashboard");
});

app.get("/incidents", (req, res) => {
  res.render("incidents");
});

app.get("/chatbot", (req, res) => {
  res.render("chatbot");
});

app.get("/blogs", (req, res) => {
  res.render("blogs");
});

app.get("/scan", (req, res) => {
  res.render("scan");
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
