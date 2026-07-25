const { MongoClient, ServerApiVersion } = require("mongodb");

const uri = "mongodb+srv://PRITI__LUTA:YOUR_PASSWORD@cluster0.tggtune.mongodb.net/?appName=Cluster0";

const client = new MongoClient(uri, {
  serverApi: {
    version: ServerApiVersion.v1,
    strict: true,
    deprecationErrors: true,
  },
});

async function run() {
  try {
    await client.connect();
    await client.db("admin").command({ ping: 1 });
    console.log("MongoDB Connected Successfully");
  } catch (err) {
    console.error(err);
  } finally {
    await client.close();
  }
}

run();