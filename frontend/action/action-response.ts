interface ActionResponse<T> {
    message: string;
    isError: boolean;
    data?: T;
}

export type { ActionResponse };