import Login from './views/Login.vue'
import NotFound from './views/404.vue'
import Home from './views/Home.vue'
import Service from './views/nav1/service.vue'
import Tag from './views/nav1/tag.vue'

let routes = [{
        path: '/login',
        component: Login,
        name: '',
        hidden: true
    },
    {
        path: '/404',
        component: NotFound,
        name: '',
        hidden: true
    },
    {
        path: '/',
        component: Home,
        name: '服务管理',
        iconCls: 'fa fa-desktop',
        leaf: true, //只有一个节点
        children: [
            { path: '/sercice', component: Service, name: '服务' }
        ]
    },

    //{ path: '/main', component: Main },
    {
        path: '/',
        component: Home,
        name: '服务',
        leaf: true, //只有一个节点
        iconCls: 'fa fa-tags', //图标样式class
        children: [
            // { path: '/main', component: Main, name: '主页', hidden: true }
            { path: '/tag', component: Tag, name: '标签' },
        ]
    },

    // {
    //     path: '/',
    //     component: Home,
    //     name: 'Charts',
    //     iconCls: 'fa fa-bar-chart',
    //     children: [
    //         { path: '/echarts', component: echarts, name: 'echarts' }
    //     ]
    // },
    {
        path: '*',
        hidden: true,
        redirect: { path: '/404' }
    }
];

export default routes;