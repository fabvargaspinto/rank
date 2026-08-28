import { z } from "zod";

export function verifySchema({schema, data}: {schema: z.ZodSchema, data: any}): { error?: string, data?: any } {
    const result = schema.safeParse(data);
    if (!result.success) {
        return {
            error: result.error.issues[0]?.message ?? result.error.message,
        };
    }
    return {
        data: result.data,
    };
}
