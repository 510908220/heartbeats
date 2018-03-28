<template>
	<section>
		<el-tag v-for="(value, key) in tag_map" :key="key" :type="info">
			{{key}}
		</el-tag>
		<!--工具条-->
		<el-col :span="24" class="toolbar" style="padding-bottom: 0px;">
			<el-form :inline="true" :model="filters">
				<el-form-item>
					<el-input v-model="filters.tag" placeholder="标签"></el-input>
				</el-form-item>
				<el-form-item>
					<el-button type="primary" v-on:click="getServices">查询</el-button>
				</el-form-item>
				<el-form-item>
					<el-button type="primary" @click="handleAdd">新增</el-button>
				</el-form-item>
			</el-form>
		</el-col>

		<!--列表-->
		<el-table :data="services" highlight-current-row v-loading="listLoading" @selection-change="selsChange" style="width: 100%;">
			<el-table-column prop="name" label="服务名" width="200">
			</el-table-column>
			<el-table-column prop="status" label="状态" width="100">
			</el-table-column>
			<el-table-column prop="tp" label="类型" width="120" sortable>
			</el-table-column>
			<el-table-column prop="value" label="值" width="120" sortable>
			</el-table-column>
			<el-table-column prop="grace" label="Grace" width="120" sortable>
			</el-table-column>
			<el-table-column prop="short_url" label="地址" width="120" sortable>
			</el-table-column>
			<el-table-column prop="last_ping.created" label="最近一次上报" width="120">
			</el-table-column>
			<el-table-column label="操作" min-width="150">
				<template scope="scope">
					<el-button size="small" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
					<el-button type="danger" size="small" @click="handleDel(scope.$index, scope.row)">删除</el-button>
				</template>
			</el-table-column>
		</el-table>

		<!--工具条-->

		<!--编辑界面-->
		<el-dialog title="编辑" v-model="editFormVisible" :close-on-click-modal="false">
			<el-form :model="editForm" label-width="80px" :rules="editFormRules" ref="editForm">
				<el-form-item label="服务名" prop="name">
					<el-input v-model="editForm.name" auto-complete="off"></el-input>
				</el-form-item>
				<el-form-item label="状态">
					<el-select v-model="editForm.status" placeholder="选择状态">
						<el-option label="running" value="running"></el-option>
						<el-option label="stoped" value="stoped"></el-option>
					</el-select>
				</el-form-item>
				<el-form-item label="类型">
					<el-select v-model="editForm.tp" placeholder="选择类型">
						<el-option label="at" value="at"></el-option>
						<el-option label="every" value="every"></el-option>
					</el-select>
				</el-form-item>

				<el-form-item label="值">
					<el-input type="textarea" v-model="editForm.value"></el-input>
				</el-form-item>
				<el-form-item label="Grace">
					<el-input type="textarea" v-model="editForm.grace"></el-input>
				</el-form-item>
				<el-form-item label="通知">
					<el-input type="textarea" v-model="editForm.notify_to"></el-input>
				</el-form-item>
				<el-form-item label="标签">
					<el-input type="textarea" v-model="editForm.tags"></el-input>
				</el-form-item>
			</el-form>
			<div slot="footer" class="dialog-footer">
				<el-button @click.native="editFormVisible = false">取消</el-button>
				<el-button type="primary" @click.native="editSubmit" :loading="editLoading">提交</el-button>
			</div>
		</el-dialog>

		<!--新增界面-->
		<el-dialog title="新增" v-model="addFormVisible" :close-on-click-modal="false">
			<el-form :model="addForm" label-width="80px" :rules="addFormRules" ref="addForm">
				<el-form-item label="服务名" prop="name">
					<el-input v-model="addForm.name" auto-complete="off"></el-input>
				</el-form-item>
				<el-form-item label="状态">
					<el-select v-model="addForm.status" placeholder="选择状态">
						<el-option label="running" value="running"></el-option>
						<el-option label="stoped" value="stoped"></el-option>
					</el-select>
				</el-form-item>
				<el-form-item label="类型">
					<el-select v-model="addForm.tp" placeholder="选择类型">
						<el-option label="at" value="at"></el-option>
						<el-option label="every" value="every"></el-option>
					</el-select>
				</el-form-item>

				<el-form-item label="值">
					<el-input type="textarea" v-model="addForm.value"></el-input>
				</el-form-item>
				<el-form-item label="Grace">
					<el-input type="textarea" v-model="addForm.grace"></el-input>
				</el-form-item>
				<el-form-item label="通知">
					<el-input type="textarea" v-model="addForm.notify_to"></el-input>
				</el-form-item>
				<el-form-item label="标签">
					<el-input type="textarea" v-model="addForm.tags"></el-input>
				</el-form-item>
			</el-form>
			<div slot="footer" class="dialog-footer">
				<el-button @click.native="addFormVisible = false">取消</el-button>
				<el-button type="primary" @click.native="addSubmit" :loading="addLoading">提交</el-button>
			</div>
		</el-dialog>
	</section>
</template>

<script>
import util from '../../common/js/util'
//import NProgress from 'nprogress'
import { listService, addService, detailService } from '../../api/api';
export default {
	data() {
		return {
			filters: {
				tag: ''
			},
			tag_map: {},
			services: [],
			total: 0,
			page: 1,
			listLoading: false,
			sels: [],//列表选中列

			editFormVisible: false,//编辑界面是否显示
			editLoading: false,
			editFormRules: {
				name: [
					{ required: true, message: '请输入服务', trigger: 'blur' }
				]
			},
			//编辑界面数据
			editForm: {
				id: 0,
				name: '',
				status: '',
				tp: '',
				value: '',
				grace: '',
				notify_to: '',
				tags: ""
			},

			addFormVisible: false,//新增界面是否显示
			addLoading: false,
			addFormRules: {
				name: [
					{ required: true, message: '请输入服务', trigger: 'blur' }
				]
			},
			//新增界面数据
			addForm: {
				name: '',
				status: '',
				tp: '',
				value: '',
				grace: '',
				notify_to: '',
				tags: ""
			}

		}
	},
	methods: {
		handleCurrentChange(val) {
			this.page = val;
			this.getServices();
		},
		//获取用户列表
		getServices() {
			let para = {
			};
			if (this.filters.tag) {
				let tag_ids = [];
				for (let tag_name of this.filters.tag.split(",")) {
					var tag_id = this.tag_map[tag_name.trim()];
					if (tag_id) {
						tag_ids.push(tag_id);
					}
				}
				para['tags'] = tag_ids.join(",");
			}
			this.listLoading = true;
			//NProgress.start();
			listService(para).then((res) => {
				var tmp_services = [];
				for (var service of res.data) {
					var tmp_tags = [];
					for (var tag of service['tags']) {
						tmp_tags.push(tag.name);
						this.tag_map[tag.name] = tag.id;
					}
					service.tags = tmp_tags.join(",");
					tmp_services.push(service);
				}
				this.services = tmp_services;
				this.listLoading = false;
				//NProgress.done();
			});
		},
		//删除
		handleDel: function(index, row) {
			this.$confirm('确认删除该记录吗?', '提示', {
				type: 'warning'
			}).then(() => {
				this.listLoading = true;
				//NProgress.start();
				let para = { id: row.id, method: 'delete' };
				detailService(para).then((res) => {
					this.listLoading = false;
					//NProgress.done();
					this.$message({
						message: '删除成功',
						type: 'success'
					});
					this.getServices();
				});
			}).catch(() => {

			});
		},
		//显示编辑界面
		handleEdit: function(index, row) {
			this.editFormVisible = true;
			this.editForm = Object.assign({}, row);
		},
		//显示新增界面
		handleAdd: function() {
			this.addFormVisible = true;
			this.addForm = {
				name: '',
				status: '',
				tp: '',
				value: '',
				grace: '',
				notify_to: '',
				tags: ''
			};
		},
		//编辑
		editSubmit: function() {
			this.$refs.editForm.validate((valid) => {
				if (valid) {
					this.$confirm('确认提交吗？', '提示', {}).then(() => {
						this.editLoading = true;
						//NProgress.start();
						let para = Object.assign({ 'method': 'put' }, this.editForm);
						delete para['last_ping'];
						detailService(para).then((res) => {
							this.editLoading = false;
							//NProgress.done();
							this.$message({
								message: '提交成功',
								type: 'success'
							});
							this.$refs['editForm'].resetFields();
							this.editFormVisible = false;
							this.getServices();
						});
					});
				}
			});
		},
		//新增
		addSubmit: function() {
			this.$refs.addForm.validate((valid) => {
				if (valid) {
					this.$confirm('确认提交吗？', '提示', {}).then(() => {
						this.addLoading = true;
						//NProgress.start();
						let para = Object.assign({}, this.addForm);
						addService(para).then((res) => {
							this.addLoading = false;
							//NProgress.done();
							this.$message({
								message: '提交成功',
								type: 'success'
							});
							this.$refs['addForm'].resetFields();
							this.addFormVisible = false;
							this.getServices();
						});
					});
				}
			});
		},
		selsChange: function(sels) {
			this.sels = sels;
		},

	},
	mounted() {
		this.getServices();
	}
}

</script>

<style scoped>

</style>
