import axios from 'axios';

let base = 'http://10.5.2.5:5827/api';

export const Server = "http://10.5.2.5:5827"

export const requestLogin = params => { return axios.post(`${base}/token/`, params) };


// 标签
export const listTag = params => { return axios.get(`${base}/tags/`, { params: params }); };
export const addTag = params => { return axios.post(`${base}/tags/`, params); };
export const detailTag = params => {
    let id = params.id;
    let method = params.method;
    delete params.id;
    delete params.method;
    let url = `${base}/tags/${id}/`;
    switch (method) {
        case 'get':
            return axios.get(url, params);
        case 'delete':
            return axios.delete(url);
        case 'patch':
            return axios.patch(url, params);
        default:
            return axios.post(url, params);
    }

};



// 服务
export const listService = params => { return axios.get(`${base}/services/`, { params: params }); };
export const addService = params => { return axios.post(`${base}/services/`, params); };
export const detailService = params => {
    let id = params.id;
    let method = params.method;
    delete params.id;
    delete params.method;
    let url = `${base}/services/${id}/`;
    switch (method) {
        case 'get':
            return axios.get(url, params);
        case 'delete':
            return axios.delete(url);
        case 'put':
            return axios.put(url, params);
        default:
            return axios.post(url, params);
    }

};


// Ping
export const listPing = params => { return axios.get(`${base}/pings/`, { params: params }); };
export const addPing = params => { return axios.post(`${base}/pings/`, params); };
export const detailPing = params => {
    let id = params.id;
    let method = params.method;
    delete params.id;
    delete params.method;
    let url = `${base}/pings/${id}/`;
    switch (method) {
        case 'get':
            return axios.get(url, params);
        case 'delete':
            return axios.delete(url);
        case 'patch':
            return axios.patch(url, params);
        default:
            return axios.post(url, params);
    }

};