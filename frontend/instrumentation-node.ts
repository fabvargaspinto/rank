import { backendUrl } from "./lib/api/client";

try {
    backendUrl();
} catch (error) {
    console.error(error);
    process.exit(1);
}
