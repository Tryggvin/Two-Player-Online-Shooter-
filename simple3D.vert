attribute vec3 a_position;
//## ADD CODE HERE ##
attribute vec3 a_normal;

uniform mat4 u_model_matrix;
uniform mat4 u_projection_matrix;
uniform mat4 u_view_matrix;
uniform vec4 u_color;

varying vec4 v_color;  //Leave the varying variables alone to begin with

void main(void)
{
	vec4 position = vec4(a_position.x, a_position.y, a_position.z, 1.0);
	//## ADD CODE HERE ##
	vec4 normal = vec4(a_normal.x, a_normal.y, a_normal.z, 0.0);
	

	position = u_model_matrix * position;
	//## ADD CODE HERE ##
	normal = u_model_matrix * normal;


	float light_factor_1 = max(dot(normalize(normal), normalize(vec4(1, 2, 3, 0))), 0.0);
	float light_factor_2 = max(dot(normalize(normal), normalize(vec4(-3, -2, -1, 0))), 0.0);
	v_color = (light_factor_1 + light_factor_2) * u_color; // ### --- Change this vector (pure white) to color variable --- #####

	// ### --- Change the projection_view_matrix to separate view and projection matrices --- ### 
	position = u_projection_matrix * (u_view_matrix * position);

	gl_Position = position;
}
// attribute vec3 a_position;

// attribute vec3 a_normal;
// attribute vec2 a_uv;

// // varying vec3 fragmentColor;
// // varying vec2 fragmentTextCoord;

// uniform mat4 u_model_matrix;
// uniform mat4 u_projection_matrix;
// uniform mat4 u_view_matrix;
// // uniform vec4 u_color;

// uniform vec4 u_eye_position;

// uniform vec4 u_light_position;

// // uniform sampler3D imageTexture; 

// // varying vec4 v_color;  
// varying vec4 v_normal;
// varying vec4 v_s;
// varying vec4 v_h;
// varying vec2 v_uv;


// void main(void)
// {
// 	vec4 position = vec4(a_position.x, a_position.y, a_position.z, 1.0);
// 	//## ADD CODE HERE ##
// 	vec4 normal = vec4(a_normal.x, a_normal.y, a_normal.z, 0.0);
	
// 	v_uv = a_uv;

// 	position = u_model_matrix * position;
// 	//## ADD CODE HERE ##
// 	v_normal = normalize(u_model_matrix * normal);

// 	v_s = normalize(u_light_position - position);

// 	vec4 v = normalize(u_eye_position - position);

// 	v_h = normalize(v_s + v);

// 	// float light_factor_1 = max(dot(normalize(normal), normalize(vec4(1, 2, 3, 0))), 0.0);
// 	// float light_factor_2 = max(dot(normalize(normal), normalize(vec4(-3, -2, -1, 0))), 0.0);
// 	// v_color = (light_factor_1 + light_factor_2) * u_color * texture(imageTexture, fragmentColor); // ### --- Change this vector (pure white) to color variable --- #####

// 	// ### --- Change the projection_view_matrix to separate view and projection matrices --- ### 
// 	// position = u_projection_matrix * (u_view_matrix * position);

// 	position = u_view_matrix * position;

// 	position = u_projection_matrix * position;


// 	gl_Position = position;
// 	// projection;
// }