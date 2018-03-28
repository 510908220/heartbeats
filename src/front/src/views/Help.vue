<template>
	<el-tabs v-model="activeName" @tab-click="handleClick">
		<el-tab-pane label="主机接入" name="first">
			<el-button type="text">
				<a target="_blank" :href="linux_monitor">Linux主机接入指南</a>
			</el-button>
			<el-button type="text">
				<a target="_blank" :href="windows_monitor">Windows主机接入指南</a>
			</el-button>
		</el-tab-pane>
		<el-tab-pane label="通知策略" name="second">通知策略</el-tab-pane>
		<el-tab-pane label="作业平台" name="third">作业平台</el-tab-pane>
		<el-tab-pane label="监控开发" name="fourth">监控开发</el-tab-pane>
	</el-tabs>
</template>
<script>
import { Server } from '../api/api';

export default {
	data() {
		return {
			activeName: 'first',
			linux_monitor: Server + '/static_django/linux_monitor.pdf',
			windows_monitor: Server + '/static_django/windows_monitor.pdf',
		};
	},
	methods: {
		handleClick(tab, event) {
			console.log(tab, event);
		}
	}
};
</script>
