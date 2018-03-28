<template>
	<section>
		<!--工具条-->
		<el-col :span="24" class="toolbar" style="padding-bottom: 0px;">
			<el-form :inline="true" :model="filters">
				<el-form-item>
					<el-input v-model="filters.name" placeholder="标签"></el-input>
				</el-form-item>
				<el-form-item>
					<el-button type="primary" v-on:click="getTags">查询</el-button>
				</el-form-item>
				<el-form-item>
					<el-button type="primary" @click="handleAdd">新增</el-button>
				</el-form-item>
			</el-form>
		</el-col>

		<!--列表-->
		<el-table :data="services" highlight-current-row v-loading="listLoading" @selection-change="selsChange" style="width: 100%;">
			<el-table-column prop="name" label="标签名" width="300">
			</el-table-column>
			<el-table-column prop="created" label="创建时间" width="200">
			</el-table-column>
			<el-table-column prop="updated" label="修改时间" width="200" sortable>
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
				<el-form-item label="标签名" prop="name">
					<el-input v-model="editForm.name" auto-complete="off"></el-input>
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
				<el-form-item label="标签名" prop="name">
					<el-input v-model="addForm.name" auto-complete="off"></el-input>
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
import { listTag, addTag, detailTag } from '../../api/api';
export default {
	data() {
		return {
			filters: {
				name: ''
			},
			services: [],
			total: 0,
			page: 1,
			listLoading: false,
			sels: [],//列表选中列

			editFormVisible: false,//编辑界面是否显示
			editLoading: false,
			editFormRules: {
				name: [
					{ required: true, message: '请输入标签名', trigger: 'blur' }
				]
			},
			//编辑界面数据
			editForm: {
				id: 0,
				name: ''
			},

			addFormVisible: false,//新增界面是否显示
			addLoading: false,
			addFormRules: {
				name: [
					{ required: true, message: '请输入标签名', trigger: 'blur' }
				]
			},
			//新增界面数据
			addForm: {
				name: ''
			}

		}
	},
	methods: {
		handleCurrentChange(val) {
			this.page = val;
			this.getTags();
		},
		//获取用户列表
		getTags() {
			let para = {

			};
			this.listLoading = true;
			//NProgress.start();
			listTag(para).then((res) => {
				this.services = res.data
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
				detailTag(para).then((res) => {
					this.listLoading = false;
					//NProgress.done();
					this.$message({
						message: '删除成功',
						type: 'success'
					});
					this.getTags();
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
				name: ''
			};
		},
		//编辑
		editSubmit: function() {
			this.$refs.editForm.validate((valid) => {
				if (valid) {
					this.$confirm('确认提交吗？', '提示', {}).then(() => {
						this.editLoading = true;
						//NProgress.start();
						let para = Object.assign({ 'method': 'patch' }, this.editForm);

						detailTag(para).then((res) => {
							this.editLoading = false;
							//NProgress.done();
							this.$message({
								message: '提交成功',
								type: 'success'
							});
							this.$refs['editForm'].resetFields();
							this.editFormVisible = false;
							this.getTags();
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
						addTag(para).then((res) => {
							this.addLoading = false;
							//NProgress.done();
							this.$message({
								message: '提交成功',
								type: 'success'
							});
							this.$refs['addForm'].resetFields();
							this.addFormVisible = false;
							this.getTags();
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
		this.getTags();
	}
}

</script>

<style scoped>

</style>
