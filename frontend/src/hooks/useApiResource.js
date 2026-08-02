import { useCallback, useEffect, useState } from "react";
import { getApiErrorMessage } from "../services/api";
export default function useApiResource(loader, deps = []) {
  const [state, setState] = useState({ data: null, error: "", loading: true });
  const reload = useCallback(async () => { setState((value) => ({ ...value, loading: true, error: "" })); try { setState({ data: await loader(), error: "", loading: false }); } catch (error) { setState({ data: null, error: getApiErrorMessage(error), loading: false }); } }, deps);
  useEffect(() => { reload(); }, [reload]); return { ...state, reload };
}
