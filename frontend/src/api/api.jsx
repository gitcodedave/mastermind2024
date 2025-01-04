import axios from 'axios';

export const API = axios.create({
  /*
  Base URL for backend server, sends cookies in request
  */
  baseURL: 'http://localhost:8000',
  withCredentials: true
});